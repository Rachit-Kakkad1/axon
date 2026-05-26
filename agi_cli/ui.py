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
    """The Synaptic Prism - A minimalist, compact neural core."""
    
    # Elegant, micro-braille and geometric frames
    IDLE = ["⎔", "✦", "⎔", "✧"]
    THINKING = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    STREAMING = ["•", "◦", "∙", "◦"]
    SWITCHING = ["×", "÷"]
    COMPRESSING = ["◰", "◱", "◲", "◳"]
    ERROR = ["⚠"]

    @staticmethod
    def get_spinner(state="idle", color="axon.core"):
        frames = getattr(Mascot, state.upper(), Mascot.IDLE)
        # Fix: Spinner takes name as first arg, frames as 'frames' kwarg is NOT supported in all rich versions
        # Standard way is to use a named spinner or custom frames as a list in the first arg
        return Spinner(frames, style=color)

def get_hud_layout(active_model: str, memory_usage: int, context_tokens: int, max_tokens: int):
    """Creates a minimalist, non-intrusive HUD."""
    # We'll make it a single line or very compact
    memory_bar = "■" * (memory_usage // 20) + "□" * (5 - memory_usage // 20)
    
    hud_text = Text.assemble(
        (" ⎔ ", "axon.core"),
        (f" {active_model.upper()} ", "axon.amber"),
        (" | ", "axon.graphite"),
        (f"MEM {memory_bar} ", "axon.violet"),
        (" | ", "axon.graphite"),
        (f"{context_tokens:,} tkn", "axon.system")
    )
    
    return Align.right(hud_text)

def print_axon_brand(console):
    """Prints a very minimalist brand signature."""
    console.print(f"\n[axon.core]AXON[/axon.core] [axon.system]v1.0.0-PRO[/axon.system]\n")

def get_response_header(model_name: str):
    """Returns a minimalist response indicator."""
    return Text.assemble(
        (f"\n {Mascot.IDLE[0]} ", "axon.core"),
        (f"{model_name.upper()} ", "axon.graphite"),
        ("— ", "axon.graphite")
    )
