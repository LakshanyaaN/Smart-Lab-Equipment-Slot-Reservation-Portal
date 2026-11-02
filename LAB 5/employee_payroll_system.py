
"""Employee payroll computation and salary disbursement module."""

import hashlib
import json
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional


PAYROLL_RECORDS: Dict[str, Dict[str, Any]] = {
    "EMP101": {"name": "David", "base_salary": 4500.0, "tax_rate": 0.15},
    "EMP102": {"name": "Elena", "base_salary": 5200.0, "tax_rate": 0.20},
    "EMP103": {"name": "Frank", "base_salary": 3800.0, "tax_rate": 0.12},
}


def process_salary(
    emp_id: str,
    bonus: float,
    transaction_logs: Optional[List[str]] = None,
) -> bool:
    """Credit a bonus to an employee and record the transaction."""
    if transaction_logs is None:
        transaction_logs = []

    if emp_id not in PAYROLL_RECORDS or bonus < 0:
        return False

    PAYROLL_RECORDS[emp_id]["base_salary"] += bonus
    transaction_logs.append(
        f"Credited bonus {bonus:.2f} to employee id {emp_id}"
    )
    return True


def deduct_penalty(emp_id: str, penalty: float) -> bool:
    """Deduct a penalty if the employee exists and the amount is valid."""
    if emp_id not in PAYROLL_RECORDS or penalty < 0:
        return False

    current_salary = PAYROLL_RECORDS[emp_id]["base_salary"]

    if penalty > current_salary:
        return False

    PAYROLL_RECORDS[emp_id]["base_salary"] -= penalty
    return True


def check_bonus_eligibility(
    emp_id: str,
    min_base: float = 4000.0,
) -> bool:
    """Check whether an employee meets the bonus eligibility threshold."""
    employee = PAYROLL_RECORDS.get(emp_id)

    if employee is None:
        return False

    return employee["base_salary"] >= min_base


def compute_net_salary(
    emp_id: str,
    deduction_rate: float = 0.15,
) -> float:
    """Calculate net salary using a validated deduction rate."""
    if emp_id not in PAYROLL_RECORDS:
        raise ValueError("Employee ID not found.")

    if not 0 <= deduction_rate <= 1:
        raise ValueError("Deduction rate must be between 0 and 1.")

    base_salary = PAYROLL_RECORDS[emp_id]["base_salary"]
    net_salary = base_salary * (1 - deduction_rate)

    return round(net_salary, 2)


def generate_employee_hash(emp_id: str) -> str:
    """Generate a SHA-256 hash for an employee identifier."""
    return hashlib.sha256(emp_id.encode("utf-8")).hexdigest()


def generate_payroll_token() -> int:
    """Generate a secure four-digit payroll token."""
    return secrets.randbelow(9000) + 1000


def export_payroll_sheet(
    filename: str = "payroll_sheet.txt",
) -> bool:
    """Export payroll records to a JSON-formatted text file."""
    try:
        output_path = Path(filename)
        output_path.write_text(
            json.dumps(PAYROLL_RECORDS, indent=4),
            encoding="utf-8",
        )
        print(f"Payroll summary exported to: {output_path}")
        return True
    except OSError as error:
        print(f"Error exporting payroll sheet: {error}")
        return False


def main() -> None:
    """Run the employee payroll demonstration."""
    transaction_logs: List[str] = []

    process_salary("EMP101", 350, transaction_logs)
    deduct_penalty("EMP102", 100)

    print(
        "Is EMP101 eligible:",
        check_bonus_eligibility("EMP101"),
    )

    print(
        "Net salary:",
        compute_net_salary("EMP101", 0.15),
    )

    print(
        "Employee Hash:",
        generate_employee_hash("EMP101"),
    )

    print("Payroll Token:", generate_payroll_token())

    print("Transaction Logs:", transaction_logs)

    export_payroll_sheet()


if __name__ == "__main__":
    main()
