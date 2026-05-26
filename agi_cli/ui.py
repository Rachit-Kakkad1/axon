from rich.theme import Theme
from rich.style import Style
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED, MINIMAL, SIMPLE
from rich.layout import Layout
from rich.align import Align
from rich.spinner import Spinner

# THE AXON PREMIUM NEURAL THEME
# Colors inspired by the plan: Obsidian, Cyan, Amber, Violet, Graphite
axon_theme = Theme({
    "axon.core": "bold #00F0FF",        # Electric Cyan
    "axon.amber": "bold #FFB000",       # Orchestration Amber
    "axon.violet": "bold #8A2BE2",      # Memory Violet
    "axon.graphite": "#2D2D30",         # System Muted
    "axon.bg": "#0A0A0B",               # Deep Obsidian
    "axon.text": "#E0E0E0",             # Off-white
    "axon.error": "bold #FF003C",       # Glitch Red
    "axon.user": "bold #00F0FF",
    "axon.system": "#666666",
    "axon.highlight": "bold #00F0FF underline"
})

class Mascot:
    """The Synaptic Prism - AXON's neural core mascot."""
    
    # Custom frames for different states
    IDLE = ["⎔", "⏧", "⏦", "⏧"]
    THINKING = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    SWITCHING = ["×", "÷", "×", "÷"]
    COMPRESSING = ["○", "◎", "●", "◎"]
    ERROR = ["!", "?", "!", "?"]

    @staticmethod
    def get_spinner(state="idle", color="axon.core"):
        frames = getattr(Mascot, state.upper(), Mascot.IDLE)
        return Spinner(None, frames=frames, style=color)

def get_hud_layout(active_model: str, memory_usage: int, context_tokens: int, max_tokens: int):
    """Creates the premium HUD layout."""
    layout = Layout()
    
    # Split into header and main body
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    
    # Header Content
    memory_bar = "■" * (memory_usage // 10) + "□" * (10 - memory_usage // 10)
    
    header_grid = Table.grid(expand=True)
    header_grid.add_column(justify="left", ratio=1)
    header_grid.add_column(justify="center", ratio=1)
    header_grid.add_column(justify="right", ratio=1)
    
    header_grid.add_row(
        Text.assemble((" ⎔ AXON CORE ", "axon.core"), (" [Sys: ONLINE]", "axon.system")),
        Text(f"ACTIVE: {active_model.upper()}", style="axon.amber"),
        Text.assemble(("MEM: ", "axon.violet"), (f"[{memory_bar}] ", "axon.violet"), (f"{memory_usage}%", "axon.text"))
    )
    
    layout["header"].update(Panel(header_grid, style="axon.graphite", box=SIMPLE))
    
    # Body Content (Metadata + Context)
    token_percent = int((context_tokens / max_tokens) * 100) if max_tokens > 0 else 0
    body_grid = Table.grid(padding=(0, 2))
    body_grid.add_row(
        Text("NEURAL STATE:", style="axon.graphite"),
        Text("COGNITIVE ROUTING ACTIVE", style="axon.core")
    )
    body_grid.add_row(
        Text("CONTEXT:", style="axon.graphite"),
        Text(f"{context_tokens:,} / {max_tokens:,} tokens ({token_percent}%)", style="axon.text")
    )
    
    layout["body"].update(Align.left(body_grid))
    
    return layout

def print_axon_brand(console):
    """Prints the premium brand logo."""
    logo = """
    [axon.core]
       ▄▀█ ▀▄▀ █▀█ █▄░█
       █▀█ █░█ █▄█ █░▀█
    [/axon.core]
    [axon.system]  NEURAL ORCHESTRATION ENGINE[/axon.system]
    """
    console.print(Align.center(logo))
    console.print("\n")

def get_response_header(model_name: str):
    """Returns a premium header for the AI response."""
    return Text.assemble(
        ("\n ⎔ ", "axon.core"),
        (f" {model_name.upper()} ", "black on #00F0FF"),
        (" ", "axon.bg")
    )
