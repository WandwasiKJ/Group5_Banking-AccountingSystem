from abc import ABC, abstractmethod
from datetime import datetime


class Customer:
    """Represents a bank customer with a unique ID and personal details."""

    def __init__(self, customer_id: str, name: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def display_details(self):
        print("\n--- Customer Details ---")
        print(f"Customer ID : {self.customer_id}")
        print(f"Name        : {self.name}")
        print(f"Email       : {self.email}")
        print(f"Accounts    : {[acc.account_number for acc in self.accounts]}")


class BankAccount(ABC):
    """Abstract base class for all bank account types."""

    def __init__(self, account_number: str, owner: Customer, balance: float = 0.0):
        self.account_number = account_number
        self.owner = owner
        self.__balance = float(balance)
        self.transaction_history = []
        self._record_transaction("Account Opened", float(balance))

    @property
    def balance(self) -> float:
        return self.__balance

    def _set_balance(self, amount: float):
        self.__balance = float(amount)

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            print("Error: Deposit amount must be positive.")
            return False

        self._set_balance(self.balance + amount)
        self._record_transaction("Deposit", amount)
        print(f"Successfully deposited ${amount:.2f}. New Balance: ${self.balance:.2f}")
        return True

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """Withdraw money from the account."""
        pass

    @abstractmethod
    def apply_account_rules(self):
        """Apply interest or fees depending on the account type."""
        pass

    def transfer(self, target_account: "BankAccount", amount: float) -> bool:
        if amount <= 0:
            print("Error: Transfer amount must be positive.")
            return False

        print(f"\nInitiating transfer of ${amount:.2f} to Account {target_account.account_number}...")

        if not self.withdraw(amount):
            print("Transfer failed: Ineligible funds or transaction rule violation.")
            return False

        if not target_account.deposit(amount):
            # In a production system, this would roll back the withdrawal.
            print("Transfer failed while crediting the destination account.")
            return False

        self._record_transaction(f"Transfer Out to {target_account.account_number}", amount)
        target_account._record_transaction(f"Transfer In from {self.account_number}", amount)
        print("Transfer completed successfully.")
        return True

    def _record_transaction(self, transaction_type: str, amount: float):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "timestamp": timestamp,
            "type": transaction_type,
            "amount": amount,
            "balance_after": self.__balance,
        }
        self.transaction_history.append(record)

    def display_details(self):
        print(f"\nAccount Number : {self.account_number}")
        print(f"Account Type   : {self.__class__.__name__}")
        print(f"Owner          : {self.owner.name} (ID: {self.owner.customer_id})")
        print(f"Current Balance: ${self.balance:.2f}")

    def display_transaction_history(self):
        print(f"\n--- Transaction History for Account {self.account_number} ---")
        if not self.transaction_history:
            print("No transactions recorded.")
            return

        for t in self.transaction_history:
            print(
                f"[{t['timestamp']}] {t['type']:<20} | "
                f"Amount: ${t['amount']:<8.2f} | Balance: ${t['balance_after']:.2f}"
            )


class SavingsAccount(BankAccount):
    """Savings account with a minimum balance requirement and interest."""

    def __init__(
        self,
        account_number: str,
        owner: Customer,
        balance: float = 0.0,
        interest_rate: float = 0.05,
        min_balance: float = 100.0,
    ):
        super().__init__(account_number, owner, balance)
        self.interest_rate = interest_rate
        self.min_balance = min_balance

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("Error: Withdrawal amount must be positive.")
            return False

        if self.balance - amount < self.min_balance:
            print(
                f"Error: Minimum balance limit reached. "
                f"You must maintain at least ${self.min_balance:.2f}."
            )
            return False

        self._set_balance(self.balance - amount)
        self._record_transaction("Withdrawal", amount)
        print(f"Successfully withdrew ${amount:.2f}. Remaining Balance: ${self.balance:.2f}")
        return True

    def calculate_interest(self) -> float:
        return self.balance * self.interest_rate

    def apply_account_rules(self):
        interest = self.calculate_interest()
        self._set_balance(self.balance + interest)
        self._record_transaction("Interest Applied", interest)
        print(f"Applied interest of ${interest:.2f} ({self.interest_rate * 100}%). New Balance: ${self.balance:.2f}")


class CurrentAccount(BankAccount):
    """Current account with overdraft support and maintenance fees."""

    def __init__(
        self,
        account_number: str,
        owner: Customer,
        balance: float = 0.0,
        overdraft_limit: float = 500.0,
        maintenance_fee: float = 15.0,
    ):
        super().__init__(account_number, owner, balance)
        self.overdraft_limit = overdraft_limit
        self.maintenance_fee = maintenance_fee

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("Error: Withdrawal amount must be positive.")
            return False

        if self.balance - amount < -self.overdraft_limit:
            print(
                f"Error: Overdraft limit exceeded. "
                f"Allowed overdraft limit is ${self.overdraft_limit:.2f}."
            )
            return False

        self._set_balance(self.balance - amount)
        self._record_transaction("Withdrawal", amount)
        print(f"Successfully withdrew ${amount:.2f}. Remaining Balance: ${self.balance:.2f}")
        return True

    def calculate_charge(self) -> float:
        return self.maintenance_fee

    def apply_account_rules(self):
        charge = self.calculate_charge()
        self._set_balance(self.balance - charge)
        self._record_transaction("Maintenance Charge", charge)
        print(f"Deducted maintenance fee of ${charge:.2f}. New Balance: ${self.balance:.2f}")


class FixedDepositAccount(BankAccount):
    """Fixed deposit account with penalties for early withdrawal."""

    def __init__(
        self,
        account_number: str,
        owner: Customer,
        balance: float = 0.0,
        interest_rate: float = 0.10,
        is_matured: bool = False,
        penalty_fee: float = 50.0,
    ):
        super().__init__(account_number, owner, balance)
        self.interest_rate = interest_rate
        self.is_matured = is_matured
        self.penalty_fee = penalty_fee

    def withdraw(self, amount: float) -> bool:
        if amount <= 0:
            print("Error: Withdrawal amount must be positive.")
            return False

        total_deduction = amount
        if not self.is_matured:
            total_deduction += self.penalty_fee
            print(
                f"Warning: Account has not matured. "
                f"An early withdrawal penalty fee of ${self.penalty_fee:.2f} applies."
            )

        if self.balance < total_deduction:
            print("Error: Insufficient balance to cover withdrawal and applicable penalty fees.")
            return False

        self._set_balance(self.balance - total_deduction)
        transaction_name = "Early Withdrawal + Penalty" if not self.is_matured else "Withdrawal"
        self._record_transaction(transaction_name, total_deduction)
        print(
            f"Successfully withdrew ${amount:.2f} "
            f"(Total deducted: ${total_deduction:.2f}). Remaining Balance: ${self.balance:.2f}"
        )
        return True

    def apply_account_rules(self):
        interest = self.balance * self.interest_rate
        self._set_balance(self.balance + interest)
        self._record_transaction("Fixed Deposit Interest", interest)
        print(f"Applied fixed deposit interest of ${interest:.2f}. New Balance: ${self.balance:.2f}")


if __name__ == "__main__":
    print("=== BANKING AND ACCOUNT MANAGEMENT SYSTEM DEMO ===")

    cust1 = Customer("C001", "Alice Smith", "alice@example.com")
    cust2 = Customer("C002", "Bob Jones", "bob@example.com")

    savings = SavingsAccount("SA101", cust1, balance=1000.0)
    current = CurrentAccount("CA201", cust1, balance=200.0)
    fixed = FixedDepositAccount("FD301", cust2, balance=5000.0, is_matured=False)

    cust1.add_account(savings)
    cust1.add_account(current)
    cust2.add_account(fixed)

    print("\n--- Testing Deposits ---")
    savings.deposit(500.0)

    print("\n--- Testing Withdrawals & Rules ---")
    savings.withdraw(1350.0)  # Should fail
    current.withdraw(600.0)    # Allows overdraft within limit
    fixed.withdraw(1000.0)     # Applies penalty because not matured

    print("\n--- Testing Transfers ---")
    savings.transfer(current, 200.0)

    print("\n--- Applying Account-Specific Interest / Charges (Polymorphism) ---")
    accounts: list[BankAccount] = [savings, current, fixed]
    for acc in accounts:
        acc.apply_account_rules()

    print("\n--- Customer Details & Account Summary ---")
    cust1.display_details()
    savings.display_details()
    savings.display_transaction_history()
    current.display_transaction_history()