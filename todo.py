import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table


TODO_FILE = Path("todos.json")

console = Console()

def load_todos() -> list[dict[str, Any]]:
    """Load todos from the JSON file."""

    if not TODO_FILE.exists():
        return []

    with TODO_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_todos(todos: list[dict[str, Any]]) -> None:
    """Save todos to the JSON file."""

    with TODO_FILE.open("w", encoding="utf-8") as file:
        json.dump(todos, file, indent=4)


def add_todo(title: str) -> None:
    """Add a new todo task."""
    if not title.strip():
        console.print("[red]✗ Task title cannot be empty.[/red]")
        return

    todos = load_todos()

    new_id = max((todo["id"] for todo in todos), default=0) + 1

    new_todo = {
        "id": new_id,
        "title": title,
        "completed": False,
        "created_at": datetime.now().isoformat(),
    }

    todos.append(new_todo)
    save_todos(todos)

    console.print(
        f"[green]✓[/green] Task added successfully: [bold]{title}[/bold]"
    )


def list_todos() -> None:
    """Display all todo tasks."""

    todos = load_todos()

    if not todos:
        console.print("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="Todo List")

    table.add_column("ID", justify="center")
    table.add_column("Task")
    table.add_column("Status", justify="center")
    table.add_column("Created At")

    for todo in todos:
        status = "✓ Done" if todo["completed"] else "○ Pending"

        table.add_row(
            str(todo["id"]),
            todo["title"],
            status,
            todo["created_at"],
        )

    console.print(table)


def complete_todo(todo_id: int) -> None:
    """Mark a todo task as completed."""

    todos = load_todos()

    for todo in todos:
        if todo["id"] == todo_id:
            todo["completed"] = True
            save_todos(todos)

            console.print(
                f"[green]✓[/green] Task {todo_id} marked as completed."
            )
            return

    console.print(f"[red]✗[/red] Task with ID {todo_id} not found.")


def delete_todo(todo_id: int) -> None:
    """Delete a todo task."""

    todos = load_todos()

    for todo in todos:
        if todo["id"] == todo_id:
            todos.remove(todo)
            save_todos(todos)

            console.print(
                f"[green]✓[/green] Task {todo_id} deleted successfully."
            )
            return

    console.print(f"[red]✗[/red] Task with ID {todo_id} not found.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2 and sys.argv[1] == "add":
        if len(sys.argv) < 3:
            console.print("[red]✗ Task title cannot be empty.[/red]")
        else:
            title = " ".join(sys.argv[2:])
            add_todo(title)

    elif len(sys.argv) == 2 and sys.argv[1] == "list":
        list_todos()

    elif len(sys.argv) == 3 and sys.argv[1] in {"done", "delete"}:
        try:
            todo_id = int(sys.argv[2])
        except ValueError:
            console.print("[red]✗ Task ID must be a number.[/red]")
            sys.exit(1)

        if sys.argv[1] == "done":
            complete_todo(todo_id)
        else:
            delete_todo(todo_id)

    else:
        console.print("[yellow]Usage:[/yellow]")
        console.print('  python todo.py add "Task title"')
        console.print("  python todo.py list")
        console.print("  python todo.py done <id>")
        console.print("  python todo.py delete <id>")