"""
IT Helpdesk Ticket Allocator.

Manages helpdesk tickets, technician assignments, ticket notes,
priority tracking, machine connectivity checks, and ticket storage.
"""

import hmac
import itertools
import json
import os
import re
import shutil
import subprocess  # nosec B404 - required for the ping functionality
from datetime import datetime


# Global ticket storage and counter
tickets = {}
TICKET_COUNTER = itertools.count(101)


def raise_ticket(user, issue_type, urgency="3", audit_trail=None):
    """Create a new helpdesk ticket and record it in the audit trail."""
    if audit_trail is None:
        audit_trail = []

    try:
        priority = int(urgency)
    except ValueError as exc:
        raise ValueError("Urgency must be an integer from 1 to 5.") from exc

    if not 1 <= priority <= 5:
        raise ValueError("Urgency must be between 1 and 5.")

    ticket_id = next(TICKET_COUNTER)

    tickets[ticket_id] = {
        "user": user,
        "issue": issue_type,
        "priority": priority,
        "tech": None,
        "notes": []
    }

    timestamp = datetime.now().isoformat(timespec="seconds")
    audit_trail.append(
        f"{user} raised #{ticket_id} at {timestamp}"
    )

    return ticket_id


def assign_ticket(ticket_id, technician):
    """Assign an existing ticket to a technician."""
    if ticket_id not in tickets:
        raise KeyError(f"Ticket {ticket_id} does not exist.")

    tickets[ticket_id]["tech"] = technician


def add_note(ticket_id, note):
    """Add a note to an existing ticket."""
    try:
        tickets[ticket_id]["notes"].append(note)
        return True
    except KeyError:
        return False


def close_ticket(ticket_id, password):
    """Close a ticket after verifying the administrator password."""
    admin_password = os.environ.get("HELPDESK_ADMIN_PASSWORD")

    if admin_password is None:
        return False

    if not hmac.compare_digest(password, admin_password):
        return False

    if ticket_id not in tickets:
        return False

    del tickets[ticket_id]
    return True


def unresolved_high_priority():
    """Return IDs of unassigned tickets with priority 4 or 5."""
    result = []

    for ticket_id, ticket in tickets.items():
        if (
            ticket["priority"] >= 4
            and ticket["tech"] is None
        ):
            result.append(ticket_id)

    return result


def ping_user_machine(hostname):
    """Ping a valid hostname once and return the process exit code."""
    hostname_pattern = (
        r"[A-Za-z0-9]"
        r"(?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?"
    )

    if not isinstance(hostname, str) or not re.fullmatch(
        hostname_pattern, hostname
    ):
        raise ValueError("Invalid hostname.")

    ping_executable = shutil.which("ping")

    if ping_executable is None:
        return 1

    ping_flag = "-n" if os.name == "nt" else "-c"

    try:
        result = subprocess.run(  # nosec B603 - validated hostname, no shell
            [ping_executable, ping_flag, "1", hostname],
            check=False,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode
    except subprocess.TimeoutExpired:
        return 1


def save_tickets(file_path="tickets.json"):
    """Save all current tickets to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as ticket_file:
        json.dump(tickets, ticket_file, indent=4)


def main():
    """Run a demonstration of the IT helpdesk ticket system."""
    audit_trail = []

    ticket_one = raise_ticket(
        "anil", "printer", "5", audit_trail
    )

    ticket_two = raise_ticket(
        "meera", "wifi", "4", audit_trail
    )

    ticket_three = raise_ticket(
        "joe", "vpn", "3", audit_trail
    )

    assign_ticket(ticket_one, "Tech-Kiran")
    add_note(ticket_one, "Called user")

    print("Unassigned high priority:", unresolved_high_priority())

    level = input(
        "Urgency for a new laptop ticket (1-5, Enter for 3): "
    ) or "3"

    try:
        raise_ticket("sana", "laptop", level, audit_trail)
    except ValueError as error:
        print(f"Invalid urgency: {error}")

    admin_password = os.environ.get("HELPDESK_ADMIN_PASSWORD")

    if admin_password:
        if close_ticket(ticket_three, admin_password):
            print(f"Ticket {ticket_three} closed successfully.")
        else:
            print(f"Could not close ticket {ticket_three}.")

    save_tickets()

    print("Audit trail:", audit_trail)
    print("Open tickets:", list(tickets.keys()))

    # Keep the variable to demonstrate that both tickets were created.
    print(f"Created tickets: {ticket_one}, {ticket_two}, {ticket_three}")


if __name__ == "__main__":
    main()
