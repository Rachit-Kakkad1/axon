import click
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Force UTF-8 on Windows for Unicode mascot/glyphs
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.spinner import Spinner
from rich.layout import Layout
from rich.align import Align
from rich.theme import Theme
from rich.box import ROUNDED, HEAVY_EDGE, SIMPLE

from agi_cli.memory.manager import MemoryManager
from agi_cli.adapters.gemini import GeminiAdapter
from agi_cli.adapters.claude import ClaudeAdapter
from agi_cli.orchestrator import Orchestrator
from agi_cli.ui import axon_theme, Mascot, get_hud_layout, render_welcome_screen, get_response_header

load_dotenv()

console = Console(theme=axon_theme)

@click.group(invoke_without_command=True)
@click.option("--db", default="memory.db", help="Path to the memory database.")
@click.option("--clear", is_flag=True, help="Clear memory before starting.")
@click.pass_context
def main(ctx, db, clear):
    """AXON - The AI runtime that never forgets."""
    if ctx.invoked_subcommand is None:
        start_chat(db, clear)

@main.command()
def login():
    """Authorize AXON with Google via OAuth2."""
    from agi_cli.auth import run_login_flow
    console.print(Panel("[axon.core]AXON AUTHORIZATION[/axon.core]", box=ROUNDED, border_style="axon.core"))
    try:
        with console.status("[axon.core]Waiting for browser authorization...[/axon.core]", spinner="bouncingBar"):
            run_login_flow()
        console.print("[bold green]✔ AXON linked successfully.[/bold green]")
    except Exception as e:
        console.print(f"[axon.error]✘ Sync failed: {e}[/axon.error]")

def start_chat(db, clear):
    memory = MemoryManager(db_path=db)
    if clear:
        memory.clear_memory()
        console.print("[axon.error]Memory synapses reset.[/axon.error]")

    adapters = [
        GeminiAdapter("gemini-1.5-flash"),
        ClaudeAdapter("claude-3-5-sonnet")
    ]
    orchestrator = Orchestrator(memory, adapters)

    # Premium welcome screen
    render_welcome_screen(
        console,
        memory,
        orchestrator.active_adapter.model_name,
        orchestrator.active_adapter.context_limit,
        os.getcwd()
    )
    
    while True:
        try:
            # Re-render HUD
            history = memory.get_messages()
            context_tokens = orchestrator.active_adapter.get_token_count(history)
            max_tokens = orchestrator.active_adapter.context_limit
            
            # Simulated memory usage for UI
            memory_usage = min(100, (context_tokens / 5000) * 100) if context_tokens < 5000 else 99
            
            skill_name = orchestrator.active_skill.name if orchestrator.active_skill else "None"
            
            hud = get_hud_layout(
                orchestrator.active_adapter.model_name,
                int(memory_usage),
                context_tokens,
                max_tokens,
                active_skill=skill_name
            )
            console.print(hud)
            
            # Show "Listening" mascot before input
            console.print(f" [axon.core]{Mascot.IDLE[0]}[/axon.core] ", end="")
            user_input = console.input("[axon.user]YOU[/axon.user] [white]»[/white] ")
            
            if user_input.lower() in ["exit", "quit"]:
                console.print("\n[axon.system]AXON going dormant...[/axon.system]")
                break
            if user_input.lower() == "clear":
                memory.clear_memory()
                console.print("[axon.error]Synapse cleared.[/axon.error]")
                continue
            if not user_input.strip():
                continue

            # Detect initial state for the spinner
            initial_state = "thinking"
            if orchestrator.active_skill:
                initial_state = orchestrator.active_skill.mascotState

            # PRE-RESPONSE STATUS (Thinking/Streaming)
            with Live(Mascot.get_spinner(initial_state), transient=True, console=console) as live:
                full_streamed_text = ""
                
                # Header for the response
                console.print(get_response_header(orchestrator.active_adapter.model_name))
                
                # Start chat stream
                for state, chunk in orchestrator.chat(user_input):
                    # Update mascot based on state
                    # If the orchestrator says THINKING, we might want to use the skill's specific thinking state
                    current_state = state.value
                    if state == State.THINKING and orchestrator.active_skill:
                        current_state = orchestrator.active_skill.mascotState
                        
                    live.update(Mascot.get_spinner(current_state))
                    
                    if "[Gemini" in chunk and "UNAUTHORIZED" in chunk:
                        console.print(Panel(chunk, border_style="axon.error", title="[bold red]AUTH ERROR[/bold red]"))
                        break
                    
                    full_streamed_text += chunk
                    console.print(chunk, end="")
                
                # FINAL POLISH: Rerender the whole response as Markdown for syntax highlighting
                if full_streamed_text.strip():
                    if "```" in full_streamed_text:
                        console.print("\n\n" + "─" * 40, style="axon.graphite")
                        console.print(Markdown(full_streamed_text))
                
                console.print(f"\n[axon.graphite]{'━' * console.width}[/axon.graphite]\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(Panel(f"[bold red]System Exception:[/bold red] {e}", box=HEAVY_EDGE, border_style="axon.error"))

    console.print("[axon.core]AXON SHUTDOWN COMPLETE.[/axon.core]")


if __name__ == "__main__":
    main()
