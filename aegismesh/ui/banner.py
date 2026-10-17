"""
AegisMesh - Cyberpunk Visual Terminal Branding.
"""

from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from aegismesh import __version__

AEGIS_LOGO = r"""
    ___    ______ _____ ____ ____   __  ___ _____ _____ __  __
   /   |  / ____// ___//  _// ___/ /  |/  // ___// ___// / / /
  / /| | / __/  / / __ / /  \__ \ / /|_/ // __/  \__ \/ /_/ / 
 / ___ |/ /___ / /_/ // /  ___/ // /  / // /___ ___/ // __  /  
/_/  |_/_____/ \____/___/ /____//_/  /_//_____//____//_/ /_/   
"""

def get_welcome_banner(port: int = 8088, upstream: str = "https://httpbin.org") -> Panel:
    text = Text()
    text.append(AEGIS_LOGO, style="bold cyan")
    text.append("\n  🛡️ Distributed AI Security Gateway & High-Throughput Proxy\n", style="bold green")
    text.append(f"  v{__version__} | Port: {port} | Upstream: {upstream}\n", style="dim white")
    text.append("  [WAF Active] • [Anti-DDoS TokenBucket] • [Semantic Cache Ready]\n", style="bold yellow")

    return Panel(
        Align.center(text),
        border_style="bright_blue",
        padding=(0, 2),
        subtitle="[bold red]Threat Shield: ONLINE[/bold red] • [bold cyan]Latency: Sub-Millisecond[/bold cyan]",
        subtitle_align="right"
    )
