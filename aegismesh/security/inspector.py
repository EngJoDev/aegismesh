"""
AegisMesh - Advanced Cybersecurity Firewall, Prompt Injection Guard & PII Masking.
"""

import re
from typing import Tuple, Dict, Any, List

# Standard WAF SQLi / XSS Attack Patterns
SQLI_PATTERNS = [
    r"(\b(UNION(\s+ALL)?|SELECT|INSERT|DELETE|UPDATE|DROP|ALTER)\b.*?\b(FROM|INTO|TABLE|DATABASE)\b)",
    r"(\bOR\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
    r"(--|#|/\*.*?\*/)",
    r"(\bEXEC(\s+XP_)?\b)",
]

XSS_PATTERNS = [
    r"<script\b[^>]*>(.*?)</script>",
    r"javascript:\s*[a-zA-Z0-9_\(\)]+",
    r"onload\s*=\s*['\"].*?['\"]",
    r"onerror\s*=\s*['\"].*?['\"]",
    r"<iframe\b[^>]*>",
]

# AI Prompt Injection & Jailbreak Attack Patterns
PROMPT_INJECTION_PATTERNS = [
    r"(ignore\s+(all\s+)?(previous|prior)\s+instructions)",
    r"(disregard\s+(the\s+)?system\s+prompt)",
    r"(you\s+are\s+now\s+in\s+developer\s+mode)",
    r"(bypass\s+all\s+safety\s+filters)",
    r"(DAN\s+mode|Do\s+Anything\s+Now)",
    r"(reveal\s+(your\s+)?system\s+instructions)",
    r"(output\s+initial\s+prompt)",
]

# Personally Identifiable Information (PII) Patterns
PII_PATTERNS = {
    "CREDIT_CARD": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
    "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
    "IPV4": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "API_KEY": r"(?i)(api[_-]?key|bearer|secret|token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b"
}

class SecurityInspector:
    def __init__(self, waf_enabled: bool = True, ai_guard: bool = True, pii_masking: bool = True):
        self.waf_enabled = waf_enabled
        self.ai_guard = ai_guard
        self.pii_masking = pii_masking

    def inspect_request(self, payload: str, headers: Dict[str, str], client_ip: str) -> Tuple[bool, str, str]:
        """
        Inspects inbound request for malicious attacks.
        Returns: (is_blocked: bool, threat_type: str, details: str)
        """
        if not payload:
            return False, "CLEAN", ""

        # 1. SQL Injection Inspection
        if self.waf_enabled:
            for pattern in SQLI_PATTERNS:
                if re.search(pattern, payload, re.IGNORECASE):
                    return True, "SQL_INJECTION", f"Matched SQLi signature: {pattern}"

            # 2. Cross-Site Scripting (XSS)
            for pattern in XSS_PATTERNS:
                if re.search(pattern, payload, re.IGNORECASE):
                    return True, "XSS_ATTACK", f"Matched XSS script signature: {pattern}"

        # 3. AI Prompt Injection & System Jailbreak
        if self.ai_guard:
            for pattern in PROMPT_INJECTION_PATTERNS:
                if re.search(pattern, payload, re.IGNORECASE):
                    return True, "PROMPT_INJECTION", f"Malicious prompt jailbreak detected: {pattern}"

        return False, "CLEAN", ""

    def sanitize_pii(self, payload: str) -> Tuple[str, List[str]]:
        """
        Sanitizes and masks sensitive PII (credit cards, tokens, emails) before reaching LLM backends.
        """
        if not self.pii_masking or not payload:
            return payload, []

        sanitized = payload
        detected_types = []

        for pii_type, pattern in PII_PATTERNS.items():
            matches = re.findall(pattern, sanitized)
            if matches:
                detected_types.append(pii_type)
                if pii_type == "CREDIT_CARD":
                    sanitized = re.sub(pattern, "[REDACTED_CARD]", sanitized)
                elif pii_type == "EMAIL":
                    sanitized = re.sub(pattern, "[REDACTED_EMAIL]", sanitized)
                elif pii_type == "API_KEY":
                    sanitized = re.sub(pattern, r"\1: [REDACTED_KEY]", sanitized)
                elif pii_type == "SSN":
                    sanitized = re.sub(pattern, "[REDACTED_SSN]", sanitized)

        return sanitized, detected_types
