import os
from datetime import datetime
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED, Box
from rich.align import Align
from rich.spinner import Spinner

# ═══════════════════════════════════════════════════════════════════════════
# THE OBSIDIAN NEURAL THEME
# A curated, premium color system for AXON
# ═══════════════════════════════════════════════════════════════════════════

axon_theme = Theme({
    "axon.core":      "bold #00F0FF",    # Electric Cyan — primary brand
    "axon.amber":     "bold #FFB000",    # Orchestration Amber — sections
    "axon.violet":    "bold #8A2BE2",    # Memory Violet — memory indicators
    "axon.graphite":  "#555555",         # Muted — borders, dividers
    "axon.bg":        "#0A0A0B",         # Deep Obsidian — background ref
    "axon.text":      "#E0E0E0",         # Off-white — primary text
    "axon.error":     "bold #FF003C",    # Glitch Red — errors
    "axon.user":      "bold #00F0FF",
    "axon.system":    "#888888",
    "axon.highlight": "bold #00F0FF underline",
    "axon.green":     "bold #00FF88",
    "axon.dim":       "#444444",
})


# ═══════════════════════════════════════════════════════════════════════════
# THE SYNAPTIC PRISM — AXON's Living Mascot
# Braille micro-animations that signal internal neural state
# ═══════════════════════════════════════════════════════════════════════════

class Mascot:
    """The Synaptic Prism — compact, state-driven neural core."""

    IDLE        = ["⎔", "✦", "⎔", "✧"]
    THINKING    = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    # Skill-specific states
    CODING      = ["⎔", "⎶", "⎔", "⎶"] # Sharp neural pulses
    RESEARCH    = ["✦", "✧", "❃", "✧"] # Branching/expanding retrieval
    ARCHITECTURE = ["⎔", "⎚", "⎔", "⎚"] # Slow deep cognition waves
    DEBUG       = ["⎔", "✘", "⎔", "✘"] # Flickering signal traces
    MEMORY      = ["○", "◎", "●", "◎"] # Collapsing neural folds

    STREAMING   = ["•", "◦", "∙", "◦"]
    SWITCHING   = ["×", "÷"]
    COMPRESSING = ["◰", "◱", "◲", "◳"]
    ERROR       = ["⚠"]

    @staticmethod
    def get_spinner(state="idle", color="axon.core"):
        frames = getattr(Mascot, state.upper(), Mascot.IDLE)
        return Spinner(frames, style=color)


# ═══════════════════════════════════════════════════════════════════════════
# WELCOME SCREEN — Premium Claude-Code-Inspired Panel
# Two-column layout: mascot + branding (left), activity + commands (right)
# ═══════════════════════════════════════════════════════════════════════════

def _build_mascot_art():
    """
    The Synaptic Prism — AXON's pixel-art neural entity.
    Gradient cyan (dimmer at extremities, brightest at core) with amber eyes.
    """
    m = Text()
    m.append("           ▄▄\n",     style="#00C8D8")    # antenna — dimmest
    m.append("         ▄████▄\n",   style="#00D8E8")    # head top
    m.append("         █",          style="#00F0FF")     # left cheek — brightest
    m.append(" ◈◈ ",               style="bold #FFB000") # eyes — amber accent
    m.append("█\n",                 style="#00F0FF")     # right cheek
    m.append("         ██████\n",   style="#00D8E8")    # body
    m.append("          █  █\n",    style="#00C8D8")    # feet — dimmest
    return m


def _fmt_ctx(limit):
    """Format context limit as human-readable string."""
    if limit >= 1_000_000:
        return f"{limit // 1_000_000}M"
    if limit >= 1_000:
        return f"{limit // 1_000}K"
    return str(limit)


def _time_ago(ts_str):
    """Convert a timestamp string to a human-readable 'Xm ago' format."""
    try:
        ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        d = datetime.now() - ts
        s = d.total_seconds()
        if s < 60:    return "just now"
        if s < 3600:  return f"{int(s // 60)}m ago"
        if s < 86400: return f"{int(s // 3600)}h ago"
        if d.days < 7:  return f"{d.days}d ago"
        if d.days < 30: return f"{d.days // 7}w ago"
        return f"{d.days // 30}mo ago"
    except Exception:
        return "recent"


def _summarize(role, content):
    """Summarize a message into a compact activity description."""
    preview = content[:30].replace("\n", " ").strip()
    if role == "user":
        return f"Query: {preview}"
    if role == "assistant":
        return "Neural response generated"
    if role == "system":
        return "Memory mesh compressed"
    return preview


def _shorten_path(p, max_len=35):
    """Truncate a filesystem path for display."""
    if len(p) <= max_len:
        return p
    return "…" + p[-(max_len - 1):]


def render_welcome_screen(console, memory, model_name, ctx_limit, cwd):
    """
    Renders the premium AXON welcome panel.

    Layout mirrors Claude Code exactly:
      LEFT  — greeting, pixel-art mascot, model info, working directory
      RIGHT — recent synapses (activity), neural capabilities (commands)

    Wrapped in a ROUNDED panel with the AXON title and tagline.
    """
    msg_count = memory.get_message_count()
    recent    = memory.get_recent_activity(limit=4)

    # ── LEFT COLUMN ───────────────────────────────────────────────────────
    left = Text()

    if msg_count > 0:
        left.append("Welcome back", style="bold white")
        left.append(", ", style="white")
        left.append("Operator", style="bold #00F0FF")
        left.append(".\n\n", style="white")
    else:
        left.append("Initializing", style="bold white")
        left.append(" neural link", style="bold #00F0FF")
        left.append("…\n\n", style="white")

    # Pixel-art mascot
    left.append_text(_build_mascot_art())
    left.append("\n")

    # Model + context + working directory
    left.append(f"   {model_name}", style="bold white")
    left.append(f" • Max {_fmt_ctx(ctx_limit)}\n", style="#888888")
    left.append(f"   {_shorten_path(cwd)}\n", style="#666666")

    # ── RIGHT COLUMN ──────────────────────────────────────────────────────
    right = Text()

    # --- Recent synapses ---
    right.append("Recent synapses\n", style="bold #FFB000")

    if recent:
        for role, content, ts in recent:
            right.append(f" {_time_ago(ts):<10}", style="#888888")
            right.append(f"{_summarize(role, content)}\n", style="#E0E0E0")
        right.append(" … /history for more\n", style="#555555")
    else:
        right.append(" No synapses recorded yet.\n", style="#555555")
        right.append(" Start a conversation to build memory.\n", style="#555555")

    right.append("\n")

    # --- Neural capabilities ---
    right.append("Neural capabilities\n", style="bold #FFB000")

    capabilities = [
        ("/models ", "switch neural pathways"),
        ("/clear  ", "reset synaptic memory"),
        ("ctrl+c  ", "go dormant"),
    ]
    for cmd, desc in capabilities:
        right.append(f" {cmd}", style="bold white")
        right.append(f"{desc}\n", style="#888888")
    right.append(" … /help for more\n", style="#555555")

    # ── ASSEMBLE PANEL ────────────────────────────────────────────────────
    inner = Table(
        show_header=False,
        show_edge=False,
        box=None,
        pad_edge=True,
        padding=(0, 2),
        expand=True,
    )
    inner.add_column("left",  ratio=2, no_wrap=False)
    inner.add_column("right", ratio=3, no_wrap=False)
    inner.add_row(left, right)

    panel = Panel(
        inner,
        title="[bold #00F0FF] AXON [/] [#888888]v1.0.0-PRO[/]",
        subtitle="[#444444]The AI Runtime That Never Forgets[/]",
        border_style="#555555",
        box=ROUNDED,
        padding=(1, 2),
        expand=True,
    )

    console.print()
    console.print(panel)

    # Bottom hint — matches Claude Code's prompt-line hint
    console.print(
        f"\n  [#00F0FF]>[/] [#777777]Type a message, or[/] "
        f"[bold white]/help[/] [#777777]for commands[/]\n"
    )


# ═══════════════════════════════════════════════════════════════════════════
# HUD — Heads-Up Display (compact status bar)
# ═══════════════════════════════════════════════════════════════════════════

def get_hud_layout(active_model, memory_usage, context_tokens, max_tokens, active_skill="None"):
    """Creates the premium Skill-aware HUD panel."""
    
    # Mascot ASCII - Central visualization (as requested in Skill System design)
    # Using a slightly simplified version of the user's requested circular art
    mascot_lines = [
        "                 ◉                                    ",
        "            ╱────────╲                                ",
        "          ╱─╱  ◎◎  ╲─╲                               ",
        "          ╲─╲──────╱─╱                               ",
        "            ╲──────╱                                 "
    ]
    
    panel_content = Text()
    panel_content.append("\n")
    for line in mascot_lines:
        panel_content.append(line + "\n", style="axon.core")
    
    panel_content.append("\n")
    panel_content.append(f"  Active Skill: ", style="axon.system")
    panel_content.append(f"{active_skill.upper()}\n", style="axon.core")
    
    panel_content.append(f"  Provider:     ", style="axon.system")
    panel_content.append(f"{active_model}\n", style="axon.amber")
    
    panel_content.append(f"  Context:      ", style="axon.system")
    panel_content.append(f"Stable\n", style="axon.green")
    
    panel_content.append(f"  Routing:      ", style="axon.system")
    panel_content.append(f"Adaptive\n", style="axon.core")

    header_text = Text.assemble(
        ("AXON Runtime", "axon.core"),
        (" " * 18),
        (f"Memory {memory_usage}%", "axon.violet")
    )

    return Panel(
        panel_content,
        title=header_text,
        border_style="axon.graphite",
        box=ROUNDED,
        width=56,
        padding=(0, 1)
    )


# ═══════════════════════════════════════════════════════════════════════════
# RESPONSE HEADER
# ═══════════════════════════════════════════════════════════════════════════

def get_response_header(model_name):
    """Returns a minimalist response indicator."""
    return Text.assemble(
        (f"\n {Mascot.IDLE[0]} ", "axon.core"),
        (f"{model_name.upper()} ", "axon.graphite"),
        ("— ", "axon.graphite"),
    )


# Legacy alias — use render_welcome_screen() instead
def print_axon_brand(console):
    console.print(f"\n[axon.core]AXON[/axon.core] [axon.system]v1.0.0-PRO[/axon.system]\n")
