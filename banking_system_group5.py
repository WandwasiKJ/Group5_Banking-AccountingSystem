
from abc import ABC, abstractmethod
from datetime import date, datetime #the program uses datetime when recording when the transaction happended
from typing import List, Optional #This discribs the type of data somethimg should contain


class Transaction:
    """Represents one transaction made on a bank account."""

    def __init__(self, transaction_type: str, amount: float, description: str):
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        return (
            f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{self.transaction_type:<10} | UGX {self.amount:,.2f} | "
            f"{self.description}"
        )


class Customer:
    """Stores customer details and the customer's bank accounts."""

    def __init__(self, customer_id: str, name: str, phone: str):
        self.__customer_id = customer_id
        self.__name = ""
        self.__phone = ""
        self.name = name
        self.phone = phone
        self._accounts: List[BankAccount] = []

    @property
    def customer_id(self) -> str:
        return self.__customer_id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        value = value.strip()
        if not value or len(value) < 2:
            raise ValueError("Customer name must contain at least 2 characters.")
        self.__name = value.title()

    @property
    def phone(self) -> str:
        return self.__phone

    @phone.setter
    def phone(self, value: str):
        value = value.strip()
        if not value.isdigit() or len(value) < 9:
            raise ValueError("Phone number must contain at least 9 digits.")
        self.__phone = value

    @property
    def accounts(self) -> List["BankAccount"]:
        # Return a copy so outside code cannot directly replace the customer's list.
        return list(self._accounts)

    def add_account(self, account: "BankAccount") -> None:
        if account not in self._accounts:
            self._accounts.append(account)

    def get_account(self, account_number: str) -> Optional["BankAccount"]:
        for account in self._accounts:
            if account.account_number == account_number:
                return account
        return None

    def __str__(self) -> str:
        return f"{self.customer_id} - {self.name} - {self.phone}"


class BankAccount(ABC):
    """Abstract superclass for all bank account types."""

    def __init__(self, account_number: str, customer: Customer, opening_balance: float = 0.0):
        self.__account_number = account_number
        self.customer = customer
        self._balance = 0.0
        self._transactions: List[Transaction] = []

        if opening_balance < 0:
            raise ValueError("Opening balance cannot be negative.")
        self._balance = opening_balance
        if opening_balance > 0:
            self._record_transaction("DEPOSIT", opening_balance, "Opening balance")

    @property
    def account_number(self) -> str:
        return self.__account_number

    @property
    def balance(self) -> float:
        # Balance can be read, but not freely changed from outside the class.
        return self._balance

    @property
    @abstractmethod
    def account_type(self) -> str:
        """Return the name of the account type."""
        raise NotImplementedError

    @abstractmethod
    def withdraw(self, amount: float) -> bool:
        """Withdraw money according to the rules of the specific account."""
        raise NotImplementedError

    @abstractmethod
    def calculate_interest(self) -> float:
        """Calculate interest according to the account type."""
        raise NotImplementedError

    @abstractmethod
    def calculate_charge(self, amount: float = 0.0) -> float:
        """Calculate account-specific transaction charges."""
        raise NotImplementedError

    def deposit(self, amount: float) -> bool:
        if amount <= 0:
            print("Invalid deposit: amount must be greater than zero.")
            return False

        self._balance += amount
        self._record_transaction("DEPOSIT", amount, "Cash deposit")
        print(f"Deposit successful. New balance: UGX {self.balance:,.2f}")
        return True

    def _record_transaction(self, transaction_type: str, amount: float, description: str) -> None:
        self._transactions.append(Transaction(transaction_type, amount, description))

    def get_transactions(self) -> List[Transaction]:
        return list(self._transactions)

    def apply_interest(self) -> float:
        interest = self.calculate_interest()
        if interest > 0:
            self._balance += interest
            self._record_transaction("INTEREST", interest, "Interest credited")
        return interest

    def charge(self, amount: float = 0.0) -> float:
        charge = self.calculate_charge(amount)
        if charge > 0:
            if self._balance < charge:
                raise ValueError("Insufficient balance to deduct the account charge.")
            self._balance -= charge
            self._record_transaction("CHARGE", charge, "Account charge")
        return charge

    def transfer_to(self, destination: "BankAccount", amount: float) -> bool:
        """Transfer money while keeping balance changes inside account objects."""
        if destination is self:
            raise ValueError("Source and destination cannot be the same account.")
        if amount <= 0:
            raise ValueError("Transfer amount must be greater than zero.")
        if not self._can_afford(amount):
            raise ValueError("Insufficient balance in source account.")

        self._balance -= amount
        self._record_transaction("TRANSFER", amount, f"Transfer to {destination.account_number}")
        destination._receive_transfer(amount, self.account_number)
        return True

    def _receive_transfer(self, amount: float, source_account_number: str) -> None:
        self._balance += amount
        self._record_transaction("TRANSFER", amount, f"Transfer from {source_account_number}")

    def _validate_withdraw_amount(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

    def _can_afford(self, amount: float) -> bool:
        return self._balance >= amount

    def __str__(self) -> str:
        return (
            f"{self.account_number} | {self.account_type:<20} | "
            f"Customer: {self.customer.name:<20} | Balance: UGX {self.balance:,.2f}"
        )


class SavingsAccount(BankAccount):
    """Savings account with interest and no monthly charge."""

    INTEREST_RATE = 0.03

    @property
    def account_type(self) -> str:
        return "Savings Account"

    def withdraw(self, amount: float) -> bool:
        try:
            self._validate_withdraw_amount(amount)
        except ValueError as error:
            print(f"Withdrawal rejected: {error}")
            return False

        if not self._can_afford(amount):
            print("Withdrawal rejected: insufficient balance.")
            return False

        self._balance -= amount
        self._record_transaction("WITHDRAW", amount, "Savings withdrawal")
        print(f"Withdrawal successful. New balance: UGX {self.balance:,.2f}")
        return True

    def calculate_interest(self) -> float:
        return self.balance * self.INTEREST_RATE

    def calculate_charge(self, amount: float = 0.0) -> float:
        return 0.0


class CurrentAccount(BankAccount):
    """Current account with a transaction charge and minimum balance rule."""

    TRANSACTION_CHARGE = 1000.0
    MINIMUM_BALANCE = 10_000.0

    @property
    def account_type(self) -> str:
        return "Current Account"

    def withdraw(self, amount: float) -> bool:
        try:
            self._validate_withdraw_amount(amount)
        except ValueError as error:
            print(f"Withdrawal rejected: {error}")
            return False

        total_needed = amount + self.TRANSACTION_CHARGE
        if self.balance - total_needed < self.MINIMUM_BALANCE:
            print(
                "Withdrawal rejected: transaction charge and minimum balance rule "
                "would be violated."
            )
            return False

        self._balance -= amount
        self._record_transaction("WITHDRAW", amount, "Current account withdrawal")
        self._balance -= self.TRANSACTION_CHARGE
        self._record_transaction("CHARGE", self.TRANSACTION_CHARGE, "Withdrawal transaction charge")
        print(f"Withdrawal successful. New balance: UGX {self.balance:,.2f}")
        return True

    def calculate_interest(self) -> float:
        return 0.0

    def calculate_charge(self, amount: float = 0.0) -> float:
        return self.TRANSACTION_CHARGE


class FixedDepositAccount(BankAccount):
    """Fixed deposit account whose funds are locked until maturity."""

    INTEREST_RATE = 0.08

    def __init__(self, account_number: str, customer: Customer, opening_balance: float, term_months: int):
        if term_months < 1:
            raise ValueError("Fixed deposit term must be at least 1 month.")
        super().__init__(account_number, customer, opening_balance)
        self.__term_months = term_months
        self.__start_date = date.today()
        # This simple calculation is suitable for the classroom project.
        month = self.__start_date.month - 1 + term_months
        year = self.__start_date.year + month // 12
        month = month % 12 + 1
        day = min(self.__start_date.day, 28)
        self.__maturity_date = date(year, month, day)

    @property
    def account_type(self) -> str:
        return "Fixed Deposit Account"

    @property
    def term_months(self) -> int:
        return self.__term_months

    @property
    def maturity_date(self) -> date:
        return self.__maturity_date

    def is_matured(self) -> bool:
        return date.today() >= self.maturity_date

    def withdraw(self, amount: float) -> bool:
        try:
            self._validate_withdraw_amount(amount)
        except ValueError as error:
            print(f"Withdrawal rejected: {error}")
            return False

        if not self.is_matured():
            print(
                f"Withdrawal rejected: fixed deposit matures on "
                f"{self.maturity_date.isoformat()}."
            )
            return False

        if not self._can_afford(amount):
            print("Withdrawal rejected: insufficient balance.")
            return False

        self._balance -= amount
        self._record_transaction("WITHDRAW", amount, "Fixed deposit withdrawal after maturity")
        print(f"Withdrawal successful. New balance: UGX {self.balance:,.2f}")
        return True

    def calculate_interest(self) -> float:
        return self.balance * self.INTEREST_RATE

    def calculate_charge(self, amount: float = 0.0) -> float:
        return 0.0


class Bank:
    """Coordinates customers, accounts and banking operations."""

    def __init__(self, name: str):
        self.name = name
        self._customers: List[Customer] = []
        self._accounts: List[BankAccount] = []
        self.__next_customer_id = 1
        self.__next_account_number = 1001

    def register_customer(self, name: str, phone: str) -> Customer:
        customer_id = f"CUS{self.__next_customer_id:04d}"
        customer = Customer(customer_id, name, phone)
        self._customers.append(customer)
        self.__next_customer_id += 1
        return customer

    def find_customer(self, customer_id: str) -> Optional[Customer]:
        for customer in self._customers:
            if customer.customer_id.lower() == customer_id.strip().lower():
                return customer
        return None

    def find_account(self, account_number: str) -> Optional[BankAccount]:
        for account in self._accounts:
            if account.account_number == account_number.strip():
                return account
        return None

    def open_account(self, customer_id: str, account_type: str, opening_balance: float = 0.0,
                     term_months: int = 1) -> BankAccount:
        customer = self.find_customer(customer_id)
        if customer is None:
            raise ValueError("Customer not found. Register the customer first.")

        if opening_balance < 0:
            raise ValueError("Opening balance cannot be negative.")

        account_number = str(self.__next_account_number)
        account_type = account_type.strip().lower()

        if account_type == "savings":
            account = SavingsAccount(account_number, customer, opening_balance)
        elif account_type == "current":
            if opening_balance < CurrentAccount.MINIMUM_BALANCE:
                raise ValueError(
                    f"Current account requires at least UGX {CurrentAccount.MINIMUM_BALANCE:,.2f}."
                )
            account = CurrentAccount(account_number, customer, opening_balance)
        elif account_type in {"fixed", "fixed deposit", "fixeddeposit"}:
            account = FixedDepositAccount(account_number, customer, opening_balance, term_months)
        else:
            raise ValueError("Invalid account type. Choose savings, current or fixed deposit.")

        self._accounts.append(account)
        customer.add_account(account)
        self.__next_account_number += 1
        return account

    def deposit(self, account_number: str, amount: float) -> bool:
        account = self.find_account(account_number)
        if account is None:
            print("Deposit rejected: account not found.")
            return False
        return account.deposit(amount)

    def withdraw(self, account_number: str, amount: float) -> bool:
        account = self.find_account(account_number)
        if account is None:
            print("Withdrawal rejected: account not found.")
            return False
        return account.withdraw(amount)

    def transfer(self, from_number: str, to_number: str, amount: float) -> bool:
        source = self.find_account(from_number)
        destination = self.find_account(to_number)

        if source is None or destination is None:
            print("Transfer rejected: both account numbers must be valid.")
            return False
        if source.account_number == destination.account_number:
            print("Transfer rejected: source and destination cannot be the same account.")
            return False
        if amount <= 0:
            print("Transfer rejected: amount must be greater than zero.")
            return False
        if not source._can_afford(amount):
            print("Transfer rejected: insufficient balance in source account.")
            return False

        try:
            source.transfer_to(destination, amount)
        except ValueError as error:
            print(f"Transfer rejected: {error}")
            return False

        print(
            f"Transfer successful: UGX {amount:,.2f} moved from "
            f"{source.account_number} to {destination.account_number}."
        )
        return True

    def customers(self) -> List[Customer]:
        return list(self._customers)

    def accounts(self) -> List[BankAccount]:
        return list(self._accounts)

    def summary(self) -> None:
        print("\n" + "=" * 78)
        print(f"{self.name.upper()} - BANKING SUMMARY")
        print("=" * 78)
        print(f"Total customers : {len(self._customers)}")
        print(f"Total accounts  : {len(self._accounts)}")
        total_balance = sum(account.balance for account in self._accounts)
        print(f"Total deposits  : UGX {total_balance:,.2f}")

        for account_type in ["Savings Account", "Current Account", "Fixed Deposit Account"]:
            accounts = [a for a in self._accounts if a.account_type == account_type]
            balance = sum(a.balance for a in accounts)
            print(f"{account_type:<22}: {len(accounts):>3} account(s), UGX {balance:,.2f}")
        print("=" * 78)


# ----------------------------- MENU / USER INTERFACE -----------------------------

def read_positive_amount(prompt: str) -> float:
    while True:
        try:
            amount = float(input(prompt).strip())
            if amount <= 0:
                print("Enter an amount greater than zero.")
                continue
            return amount
        except ValueError:
            print("Invalid amount. Enter a numeric value.")


def read_non_negative_amount(prompt: str) -> float:
    while True:
        try:
            amount = float(input(prompt).strip())
            if amount < 0:
                print("Amount cannot be negative.")
                continue
            return amount
        except ValueError:
            print("Invalid amount. Enter a numeric value.")


def show_account(account: BankAccount) -> None:
    print("\n" + "-" * 78)
    print("ACCOUNT DETAILS")
    print("-" * 78)
    print(f"Account number : {account.account_number}")
    print(f"Account type   : {account.account_type}")
    print(f"Customer       : {account.customer.name} ({account.customer.customer_id})")
    print(f"Balance        : UGX {account.balance:,.2f}")

    if isinstance(account, FixedDepositAccount):
        print(f"Term           : {account.term_months} month(s)")
        print(f"Maturity date  : {account.maturity_date.isoformat()}")
        print(f"Matured        : {'Yes' if account.is_matured() else 'No'}")
    print("-" * 78)


def show_transaction_history(account: BankAccount) -> None:
    print(f"\nTRANSACTION HISTORY - ACCOUNT {account.account_number}")
    print("-" * 78)
    transactions = account.get_transactions()
    if not transactions:
        print("No transactions recorded.")
    else:
        for transaction in transactions:
            print(transaction)


def choose_account_type() -> str:
    print("1. Savings Account")
    print("2. Current Account")
    print("3. Fixed Deposit Account")
    choice = input("Choose account type: ").strip()
    return {"1": "savings", "2": "current", "3": "fixed"}.get(choice, "invalid")


def menu(bank: Bank) -> None:
    while True:
        print("\n" + "=" * 78)
        print(f"{bank.name.upper()} - MAIN MENU")
        print("=" * 78)
        print("1. Register customer")
        print("2. Open bank account")
        print("3. Deposit money")
        print("4. Withdraw money")
        print("5. Transfer money")
        print("6. Display account details")
        print("7. Display customer's accounts")
        print("8. Display transaction history")
        print("9. Calculate/apply interest")
        print("10. Calculate account charge")
        print("11. Display all accounts")
        print("12. Display bank summary")
        print("0. Exit")

        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                name = input("Customer name: ").strip()
                phone = input("Phone number: ").strip()
                customer = bank.register_customer(name, phone)
                print(f"Customer registered successfully. Customer ID: {customer.customer_id}")

            elif choice == "2":
                customer_id = input("Customer ID: ").strip()
                account_type = choose_account_type()
                if account_type == "invalid":
                    print("Invalid account type.")
                    continue
                opening_balance = read_non_negative_amount("Opening balance (UGX): ")
                term = 1
                if account_type == "fixed":
                    while True:
                        try:
                            term = int(input("Fixed deposit term (months): ").strip())
                            if term < 1:
                                raise ValueError
                            break
                        except ValueError:
                            print("Enter a whole number of at least 1 month.")
                account = bank.open_account(customer_id, account_type, opening_balance, term)
                print(f"Account opened successfully. Account number: {account.account_number}")

            elif choice == "3":
                account_number = input("Account number: ").strip()
                amount = read_positive_amount("Deposit amount (UGX): ")
                bank.deposit(account_number, amount)

            elif choice == "4":
                account_number = input("Account number: ").strip()
                amount = read_positive_amount("Withdrawal amount (UGX): ")
                bank.withdraw(account_number, amount)

            elif choice == "5":
                from_number = input("Source account number: ").strip()
                to_number = input("Destination account number: ").strip()
                amount = read_positive_amount("Transfer amount (UGX): ")
                bank.transfer(from_number, to_number, amount)

            elif choice == "6":
                account = bank.find_account(input("Account number: ").strip())
                if account is None:
                    print("Account not found.")
                else:
                    show_account(account)

            elif choice == "7":
                customer = bank.find_customer(input("Customer ID: ").strip())
                if customer is None:
                    print("Customer not found.")
                else:
                    print(f"\nACCOUNTS FOR {customer.name}")
                    if not customer.accounts:
                        print("No accounts found.")
                    for account in customer.accounts:
                        print(account)

            elif choice == "8":
                account = bank.find_account(input("Account number: ").strip())
                if account is None:
                    print("Account not found.")
                else:
                    show_transaction_history(account)

            elif choice == "9":
                account = bank.find_account(input("Account number: ").strip())
                if account is None:
                    print("Account not found.")
                    continue
                interest = account.apply_interest()
                print(f"Interest calculated/applied: UGX {interest:,.2f}")
                print(f"New balance: UGX {account.balance:,.2f}")

            elif choice == "10":
                account = bank.find_account(input("Account number: ").strip())
                if account is None:
                    print("Account not found.")
                    continue
                charge = account.calculate_charge()
                print(f"Applicable account charge: UGX {charge:,.2f}")

            elif choice == "11":
                if not bank.accounts():
                    print("No accounts have been opened.")
                else:
                    print("\nALL BANK ACCOUNTS")
                    print("-" * 78)
                    for account in bank.accounts():
                        print(account)

            elif choice == "12":
                bank.summary()

            elif choice == "0":
                print("Thank you for using the banking system. Goodbye!")
                break

            else:
                print("Invalid menu choice. Please choose an option from the menu.")

        except ValueError as error:
            print(f"Operation rejected: {error}")
        except Exception as error:
            print(f"Unexpected error: {error}")


if __name__ == "__main__":
    bank = Bank("UCU Community Bank")
    menu(bank)
