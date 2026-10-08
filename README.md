# Group 5 Banking and Account Management System

A menu-driven Python banking application demonstrating object-oriented programming concepts. The program runs in the terminal and models customers, bank accounts, and account transactions for UCU Community Bank.

## Features

- Register customers and open savings, current, and fixed-deposit accounts.
- Deposit, withdraw, and transfer money between accounts.
- View account details, transaction history, customer accounts, and a bank summary.
- Calculate and apply account-specific interest and charges.
- Validate customer information and reject invalid banking operations.
- Demonstrate encapsulation, abstraction, inheritance, polymorphism, and object relationships.

## Requirements

- Python 3.9 or newer
- No third-party packages

## Run

From the project directory, run:

```bash
python banking_system_group5.py
```

On Windows, you can also use:

```powershell
py banking_system_group5.py
```

Follow the numbered menu options. Enter `0` to exit.

## Account Types

- **Savings account:** earns interest and permits withdrawals subject to available funds.
- **Current account:** applies a transaction charge and enforces its minimum-balance rule.
- **Fixed-deposit account:** earns interest and restricts withdrawals until its maturity date.

All displayed account amounts are in UGX.