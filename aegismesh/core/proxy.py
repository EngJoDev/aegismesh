"""
AegisMesh - Real-Time High-Performance Gateway Core Proxy.
"""

import time
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Dict, Any, List

from aegismesh.core.config import Config
from aegismesh.security.inspector import SecurityInspector
from aegismesh.limiter.rate_limiter import TokenBucketRateLimiter
from aegismesh.cache.semantic_cache import SemanticCache

# Global Telemetry Metrics
METRICS = {
    "total_requests": 0,
    "blocked_attacks": 0,
    "rate_limited": 0,
    "cache_hits": 0,
    "pii_redacted": 0,
    "threat_logs": []
}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded high-concurrency HTTP Server."""
    daemon_threads = True

class GatewayRequestHandler(BaseHTTPRequestHandler):
    config: Config = Config()
    inspector: SecurityInspector = SecurityInspector()
    rate_limiter: TokenBucketRateLimiter = TokenBucketRateLimiter(rate_per_second=10.0, burst_capacity=20)
    cache: SemanticCache = SemanticCache()

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")

    def _handle_request(self, method: str):
        global METRICS
        client_ip = self.client_address[0]
        start_time = time.time()
        METRICS["total_requests"] += 1

        # 1. Built-in Health & Dashboard Metrics Endpoints
        if self.path == "/_aegis/health":
            self._send_json(200, {"status": "HEALTHY", "gateway": "AegisMesh", "version": "0.1.0"})
            return

        if self.path in ("/_aegis/dashboard", "/_aegis/"):
            try:
                import os
                html_path = os.path.join(os.path.dirname(__file__), "..", "dashboard", "static", "index.html")
                with open(html_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self._send_json(500, {"error": "Dashboard template missing", "details": str(e)})
            return

        if self.path == "/_aegis/metrics":
            cache_stats = self.cache.stats()
            self._send_json(200, {
                "metrics": METRICS,
                "cache": cache_stats,
                "rate_limiter": {"active_ips": len(self.rate_limiter.buckets)},
                "uptime_seconds": round(time.time() - SERVER_START_TIME, 1)
            })
            return

        # 2. Rate Limiting Check (Anti-DDoS)
        allowed, remaining = self.rate_limiter.allow_request(client_ip)
        if not allowed:
            METRICS["rate_limited"] += 1
            METRICS["threat_logs"].append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ip": client_ip,
                "type": "RATE_LIMIT_EXCEEDED",
                "path": self.path
            })
            self._send_json(429, {
                "error": "Too Many Requests",
                "message": "Anti-DDoS Rate limit threshold exceeded. Retry shortly.",
                "client_ip": client_ip
            })
            return

        # 3. Read Request Body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8", errors="ignore") if content_length > 0 else ""

        # 4. Security WAF & AI Prompt Injection Inspection
        is_blocked, threat_type, details = self.inspector.inspect_request(
            payload=body,
            headers=dict(self.headers),
            client_ip=client_ip
        )

        if is_blocked:
            METRICS["blocked_attacks"] += 1
            threat_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ip": client_ip,
                "type": threat_type,
                "details": details,
                "path": self.path
            }
            METRICS["threat_logs"].append(threat_entry)
            self._send_json(403, {
                "error": "Forbidden - Security Violation",
                "threat_type": threat_type,
                "details": details,
                "protected_by": "AegisMesh WAF & AI Shield"
            })
            return

        # 5. PII Masking
        sanitized_body, detected_pii = self.inspector.sanitize_pii(body)
        if detected_pii:
            METRICS["pii_redacted"] += len(detected_pii)

        # 6. Semantic Cache Lookup (for read queries or AI payloads)
        cached_resp = self.cache.get(method, self.path, sanitized_body)
        if cached_resp:
            METRICS["cache_hits"] += 1
            self._send_json(200, cached_resp, extra_headers={"X-Aegis-Cache": "HIT"})
            return

        # 7. Proxy Forward to Upstream
        upstream_base = self.config.get("upstream", "default_target", "https://httpbin.org")
        target_url = f"{upstream_base.rstrip('/')}{self.path}"

        headers_to_forward = {k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length")}
        headers_to_forward["X-Forwarded-For"] = client_ip
        headers_to_forward["X-Protected-By"] = "AegisMesh-0.1.0"

        try:
            resp = requests.request(
                method=method,
                url=target_url,
                headers=headers_to_forward,
                data=sanitized_body.encode("utf-8") if sanitized_body else None,
                timeout=self.config.get("upstream", "timeout_seconds", 15)
            )

            # Store in cache if successful response
            if resp.status_code == 200:
                try:
                    resp_json = resp.json()
                    self.cache.set(method, self.path, sanitized_body, resp_json)
                except Exception:
                    pass

            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() not in ("content-length", "transfer-encoding", "content-encoding"):
                    self.send_header(k, v)
            self.send_header("X-Aegis-Latency-Ms", str(round((time.time() - start_time) * 1000, 2)))
            self.send_header("X-Aegis-Cache", "MISS")
            self.end_headers()
            self.wfile.write(resp.content)

        except Exception as e:
            self._send_json(502, {"error": "Bad Gateway", "upstream_error": str(e)})

    def _send_json(self, status_code: int, data: Dict[str, Any], extra_headers: Dict[str, str] = None):
        body_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body_bytes)))
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body_bytes)

    def log_message(self, format, *args):
        # Suppress noisy standard HTTP logs, handled by Aegis UI console
        return

SERVER_START_TIME = time.time()
