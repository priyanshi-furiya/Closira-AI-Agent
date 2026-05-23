"""CLI entry point for the Closira AI Customer Support Agent.

Run with: python -m src.main
"""

import sys
import os

# Fix Windows encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass


from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

from .agent import ClosiraAgent
from .stages.summary import format_summary_display


# ── Rich Console ──────────────────────────────────────────────────────────
console = Console()


def print_header():
    """Display the application header banner."""
    header = (
        "[bold magenta]🌸 BLOOM AESTHETICS CLINIC[/bold magenta]\n"
        "[dim]AI Customer Support Agent — Powered by Closira[/dim]\n"
        "[dim italic]Type [bold]quit[/bold] or [bold]bye[/bold] to end the session[/dim italic]"
    )
    console.print(
        Panel(
            header,
            title="[bold white]✨ Closira AI[/bold white]",
            border_style="magenta",
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
        )
    )


def print_agent_message(text: str):
    """Display an agent response in a styled panel."""
    console.print(
        Panel(
            Markdown(text),
            title="[bold cyan]🤖 Bloom[/bold cyan]",
            border_style="cyan",
            padding=(0, 2),
        )
    )


def print_metadata(agent_response):
    """Display response metadata (confidence, intent, escalation flags)."""
    if not agent_response:
        return

    parts = []

    # Confidence indicator with colour coding
    conf = agent_response.confidence
    if conf >= 0.8:
        conf_style = "green"
    elif conf >= 0.6:
        conf_style = "yellow"
    else:
        conf_style = "red"
    parts.append(f"[{conf_style}]Confidence: {conf:.0%}[/{conf_style}]")

    # Detected intent
    if agent_response.detected_intent:
        parts.append(f"[dim]Intent: {agent_response.detected_intent}[/dim]")

    # Escalation flag
    if agent_response.escalation_needed:
        parts.append(
            f"[red bold]⚠ ESCALATED: {agent_response.escalation_reason}[/red bold]"
        )

    # SOP scope flag
    if not agent_response.is_in_sop:
        parts.append("[yellow]⚠ Outside SOP scope[/yellow]")

    console.print("  " + " │ ".join(parts))


def main():
    """Run the interactive conversation loop."""
    print_header()
    console.print()

    # ── Initialise agent ──────────────────────────────────────────────
    try:
        console.print("  [dim]⚙️  Initialising AI agent...[/dim]")
        agent = ClosiraAgent()
        console.print("  [green]✅ Agent ready![/green]\n")
    except Exception as e:
        console.print(f"\n  [red bold]❌ Failed to initialise agent: {e}[/red bold]")
        console.print(
            "  [yellow]Please check your MISTRAL_API_KEY and try again.[/yellow]\n"
        )
        sys.exit(1)

    # ── Display greeting ──────────────────────────────────────────────
    greeting = agent.get_greeting()
    print_agent_message(greeting)

    # ── Conversation loop ─────────────────────────────────────────────
    while True:
        try:
            # Get user input
            console.print()
            user_input = console.input("[bold green]You:[/bold green] ").strip()

            if not user_input:
                continue

            # Process message through the agent
            response, metadata = agent.process_message(user_input)

            # Display the response
            print_agent_message(response)

            # Display metadata bar
            print_metadata(metadata)

            # Check if conversation ended
            if agent.is_ended:
                console.print(
                    "\n  [dim italic]⏳ Generating conversation summary...[/dim italic]\n"
                )
                summary = agent.generate_summary()

                # Display summary
                summary_text = format_summary_display(summary)
                console.print(
                    Panel(
                        summary_text,
                        title="[bold yellow]📋 Session Summary[/bold yellow]",
                        border_style="yellow",
                        box=box.HEAVY,
                        padding=(1, 2),
                    )
                )

                console.print(
                    "\n  [magenta bold]👋 Session ended. Thank you![/magenta bold]\n"
                )
                break

        except KeyboardInterrupt:
            # Graceful handling of Ctrl+C
            console.print(
                "\n\n  [dim italic]⏳ Generating conversation summary...[/dim italic]\n"
            )
            try:
                summary = agent.generate_summary()
                summary_text = format_summary_display(summary)
                console.print(
                    Panel(
                        summary_text,
                        title="[bold yellow]📋 Session Summary[/bold yellow]",
                        border_style="yellow",
                        box=box.HEAVY,
                        padding=(1, 2),
                    )
                )
            except Exception:
                console.print("  [dim]Could not generate summary.[/dim]")

            console.print(
                "\n  [magenta bold]👋 Session interrupted. Goodbye![/magenta bold]\n"
            )
            break

        except Exception as e:
            console.print(f"\n  [red]❌ Error: {e}[/red]")
            console.print(
                "  [yellow]Please try again or type 'quit' to exit.[/yellow]\n"
            )


if __name__ == "__main__":
    main()
