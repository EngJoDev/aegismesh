"""
AegisMesh - CLI Management Console.
"""

import click
from rich.console import Console
from rich.table import Table

from aegismesh import __version__
from aegismesh.core.config import Config
from aegismesh.core.proxy import ThreadedHTTPServer, GatewayRequestHandler
from aegismesh.ui.banner import get_welcome_banner

console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--version", "-v", is_flag=True, help="Show AegisMesh version.")
def main(ctx: click.Context, version: bool):
    """AegisMesh - Distributed AI Security Gateway & Threat Shield."""
    if version or ctx.invoked_subcommand is None:
        console.print(get_welcome_banner())
        if ctx.invoked_subcommand is None:
            console.print("[dim]Use [bold cyan]aegismesh start[/bold cyan] to launch the gateway proxy.[/dim]\n")

@main.command()
@click.option("--port", "-p", default=8088, help="Gateway listening port (default: 8088)")
@click.option("--upstream", "-u", default="https://httpbin.org", help="Target upstream API server")
def start(port: int, upstream: str):
    """Start the AegisMesh Gateway Proxy Server."""
    console.print(get_welcome_banner(port=port, upstream=upstream))
    
    cfg = Config()
    cfg.data["server"]["port"] = port
    cfg.data["upstream"]["default_target"] = upstream
    
    server_address = ("0.0.0.0", port)
    httpd = ThreadedHTTPServer(server_address, GatewayRequestHandler)
    
    console.print(f"[bold green]✔ AegisMesh Core listening on http://0.0.0.0:{port}[/bold green]")
    console.print(f"[bold cyan]⚡ Live SOC Dashboard: http://localhost:{port}/_aegis/dashboard[/bold cyan]")
    console.print("[dim]Press Ctrl+C to terminate gateway safely.[/dim]\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]▲ Shutting down AegisMesh gateway gracefully...[/bold yellow]")
        httpd.server_close()
        console.print("[bold green]✔ Gateway stopped.[/bold green]")

if __name__ == "__main__":
    main()
