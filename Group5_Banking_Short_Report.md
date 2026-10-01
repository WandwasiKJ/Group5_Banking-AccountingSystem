# GROUP 5: BANKING AND ACCOUNT MANAGEMENT SYSTEM

## 1. Introduction

This project implements a small object-oriented banking system using Python. The system allows a bank to register customers, open different types of accounts, deposit and withdraw money, transfer money between valid accounts, display account details, view transaction history, and calculate account-specific interest or charges.

The design follows the assignment requirements for abstraction, encapsulation, inheritance, polymorphism, object relationships, validation, and object collaboration.

## 2. Main Classes and Responsibilities

### Bank
The `Bank` class coordinates the application. It stores registered customers and bank accounts and provides operations such as registration, account creation, deposits, withdrawals, transfers, searching, and summaries.

### Customer
The `Customer` class represents a bank customer. It stores customer identification, name, phone number, and the customer's accounts. It also provides methods for adding and finding accounts.

### BankAccount
`BankAccount` is an abstract base class. It contains common account information and operations such as account number, balance, deposit, transaction recording, and access to transaction history. It also defines abstract methods that account subclasses must implement.

### SavingsAccount
A savings account earns interest at the defined savings rate and allows withdrawals when sufficient funds are available.

### CurrentAccount
A current account applies a transaction charge and enforces a minimum balance when a withdrawal is made.

### FixedDepositAccount
A fixed deposit account stores a term and maturity date. Withdrawal is rejected before maturity. It calculates interest using its own fixed-deposit rate.

### Transaction
The `Transaction` class represents an individual transaction and stores its type, amount, description, and timestamp.

## 3. Encapsulation

Encapsulation is demonstrated in several places. The customer ID, name, and phone are private attributes using double underscores. The account number is also private. The account balance is protected and is exposed through a read-only property rather than being freely changed from outside the account object.

Setters are used for customer name and phone so that invalid values can be rejected. Account methods such as `deposit()`, `withdraw()`, `apply_interest()` and `charge()` control changes to the balance.

## 4. Object Relationships

The system uses meaningful relationships:

- A `Bank` manages many `Customer` objects.
- A `Customer` owns zero or more `BankAccount` objects.
- A `BankAccount` records zero or more `Transaction` objects.
- A `BankAccount` belongs to one `Customer`.
- The `Bank` depends on account objects to perform banking operations.

These relationships support the actual behaviour of the banking system rather than being added only to satisfy an OOP requirement.

## 5. Inheritance

The abstract `BankAccount` class is the superclass for:

- `SavingsAccount`
- `CurrentAccount`
- `FixedDepositAccount`

This hierarchy allows common account behaviour to be shared while account-specific rules are implemented in the subclasses.

## 6. Abstraction

`BankAccount` inherits from Python's `ABC` and contains abstract methods such as `withdraw()`, `calculate_interest()`, `calculate_charge()`, and the abstract `account_type` property. Therefore, each concrete account type is required to provide its own implementation.

## 7. Method Overriding and Polymorphism

Each account subclass overrides `withdraw()`, `calculate_interest()`, and `calculate_charge()`.

For example, the same call:

```python
account.calculate_interest()
```

can produce different results depending on whether `account` refers to a `SavingsAccount`, `CurrentAccount`, or `FixedDepositAccount`.

Similarly, `account.withdraw(amount)` follows different rules for the three account types. This demonstrates polymorphism because the program can work with a `BankAccount` reference while the actual subclass determines the behaviour.

## 8. Validation and Invalid Operations

The application validates important operations, including:

- Empty or very short customer names.
- Invalid phone numbers.
- Negative opening balances.
- Invalid account types.
- Current accounts opened below the required minimum balance.
- Zero or negative deposits.
- Withdrawals exceeding available funds.
- Withdrawals from fixed deposits before maturity.
- Transfers involving invalid accounts.
- Transfers to the same account.
- Transfers with non-positive amounts.

Clear rejection messages are displayed when an operation is invalid.

## 9. Menu and Functional Requirements

The menu allows the user to:

1. Register customers.
2. Open accounts.
3. Deposit money.
4. Withdraw money.
5. Transfer money.
6. Display account details.
7. Display a customer's accounts.
8. Display transaction history.
9. Calculate/apply interest.
10. Calculate account charges.
11. Display all accounts.
12. Display a bank summary.
13. Exit the system.

## 10. Demonstration Plan

During the class demonstration, the group should show the following sequence:

1. Register at least two customers.
2. Open a savings account for one customer.
3. Open a current account for another customer.
4. Open a fixed deposit account.
5. Deposit money into an account.
6. Make a successful withdrawal.
7. Attempt a withdrawal that violates an account rule and show the rejection message.
8. Transfer money between two valid accounts.
9. Display an account balance and details.
10. Display transaction history.
11. Apply/calculate interest to demonstrate polymorphism.
12. Display the final bank summary.

## 11. Conclusion

The project demonstrates the major object-oriented programming concepts required by the practical assignment. The application is divided into cooperating classes, protects important object state, uses meaningful relationships, applies inheritance and abstraction, and demonstrates polymorphism through account-specific behaviour. Validation is included so that invalid banking operations are rejected with clear messages.
