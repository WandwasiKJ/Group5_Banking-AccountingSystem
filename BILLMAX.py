
from abc import ABC, abstractmethod
from math import isfinite


def check_amount(value):
    """Convert input to a positive number or raise a clear error."""
    try:
        amount = float(str(value).replace(",", ""))
    except ValueError:
        raise ValueError("Amount must be a number.")
    if not isfinite(amount) or amount <= 0:
        raise ValueError("Amount must be greater than zero.")
    return round(amount, 2)


# ------------------------------------------------------------------ Customer
class Customer:
    def __init__(self, customer_id, name, phone):
        self._customer_id = customer_id
        self.name = name              # validated by the setters below
        self.phone = phone
        self.accounts = []            # association: one customer -> many accounts

    @property
    def customer_id(self):
        return self._customer_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if len(value.strip()) < 2:
            raise ValueError("Name must have at least 2 characters.")
        self._name = value.strip()

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        digits = value.strip().lstrip("+")
        if not digits.isdigit() or not 9 <= len(digits) <= 12:
            raise ValueError("Phone must be 9-12 digits (optional leading +).")
        self._phone = value.strip()


# ------------------------------------------------------------------ Accounts
class BankAccount(ABC):
    """Abstract base class. The balance is private and changes only through _change()."""
    TYPE = "Account"
    MIN_OPENING = 0

    def __init__(self, number, owner, opening_deposit):
        if opening_deposit < self.MIN_OPENING:
            raise ValueError(f"{self.TYPE} account needs at least {self.MIN_OPENING:,.0f} to open.")
        self._number = number
        self._owner = owner
        self._history = []            # transaction history
        self.__balance = 0            # private attribute
        self._change(opening_deposit, "OPENING")

    @property
    def number(self):
        return self._number

    @property
    def owner(self):
        return self._owner

    @property
    def balance(self):                # read-only: no setter
        return self.__balance

    @property
    def history(self):
        return list(self._history)    # a copy, so outsiders cannot edit it

    def _change(self, amount, kind):  # protected: the only place the balance changes
        self.__balance += amount
        self._history.append(f"{kind:<10} {amount:>+15,.2f}   balance {self.__balance:,.2f}")

    def check_deposit(self, amount):  # subclasses may refuse deposits
        pass

    def deposit(self, amount):
        amount = check_amount(amount)
        self.check_deposit(amount)
        self._change(amount, "DEPOSIT")

    def month_end(self):
        interest, charge = self.calculate_interest(), self.calculate_charge()
        if interest:
            self._change(interest, "INTEREST")
        if charge:
            self._change(-charge, "CHARGE")
        return interest, charge

    def details(self):
        return (f"{self._number} | {self.TYPE} | Owner: {self._owner.name} | "
                f"Balance: {self.__balance:,.2f}")

    @abstractmethod
    def withdraw(self, amount):
        """Each account type enforces its own withdrawal rules."""

    @abstractmethod
    def calculate_interest(self):
        """Monthly interest."""

    @abstractmethod
    def calculate_charge(self):
        """Monthly charge."""


class SavingsAccount(BankAccount):
    TYPE = "Savings"
    MIN_OPENING = 50000
    MIN_BALANCE = 20000

    def withdraw(self, amount):
        amount = check_amount(amount)
        if self.balance - amount < self.MIN_BALANCE:
            raise ValueError(f"Balance must stay at or above {self.MIN_BALANCE:,.0f}.")
        self._change(-amount, "WITHDRAW")

    def calculate_interest(self):
        return round(self.balance * 0.05 / 12, 2)       # 5% per year

    def calculate_charge(self):
        return 0


class CurrentAccount(BankAccount):
    TYPE = "Current"
    MIN_OPENING = 100000
    OVERDRAFT = 500000

    def withdraw(self, amount):
        amount = check_amount(amount)
        if self.balance - amount < -self.OVERDRAFT:
            raise ValueError(f"Overdraft limit of {self.OVERDRAFT:,.0f} would be exceeded.")
        self._change(-amount, "WITHDRAW")

    def calculate_interest(self):
        return 0

    def calculate_charge(self):
        return 10000                                     # monthly fee


class FixedDepositAccount(BankAccount):
    TYPE = "Fixed Deposit"
    MIN_OPENING = 1000000
    TERM_MONTHS = 3

    def __init__(self, number, owner, opening_deposit):
        self._months = 0
        super().__init__(number, owner, opening_deposit)

    def check_deposit(self, amount):
        raise ValueError("Fixed deposit accounts do not accept further deposits.")

    def withdraw(self, amount):
        amount = check_amount(amount)
        if self._months < self.TERM_MONTHS:
            raise ValueError(f"Locked: matures after {self.TERM_MONTHS} months "
                             f"({self.TERM_MONTHS - self._months} remaining).")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self._change(-amount, "WITHDRAW")

    def calculate_interest(self):
        if self._months >= self.TERM_MONTHS:
            return 0
        return round(self.balance * 0.12 / 12, 2)        # 12% per year

    def calculate_charge(self):
        return 0

    def month_end(self):
        result = super().month_end()
        self._months += 1
        return result


# ------------------------------------------------------------------ Bank
class Bank:
    TYPES = {"1": ("SAV", SavingsAccount), "2": ("CUR", CurrentAccount), "3": ("FDA", FixedDepositAccount)}

    def __init__(self):
        self.customers = {}           # aggregation: bank has customers
        self.accounts = {}            # aggregation: bank has accounts

    def register_customer(self, name, phone):
        customer = Customer(f"C{len(self.customers) + 1:03d}", name, phone)
        self.customers[customer.customer_id] = customer
        return customer

    def find_customer(self, customer_id):
        customer = self.customers.get(customer_id.strip().upper())
        if customer is None:
            raise ValueError("Customer not found.")
        return customer

    def find_account(self, number):
        account = self.accounts.get(number.strip().upper())
        if account is None:
            raise ValueError("Account not found.")
        return account

    def open_account(self, customer_id, type_choice, opening_deposit):
        if type_choice not in self.TYPES:
            raise ValueError("Choose 1, 2 or 3.")
        customer = self.find_customer(customer_id)
        prefix, account_class = self.TYPES[type_choice]
        number = f"{prefix}{len(self.accounts) + 1:03d}"
        account = account_class(number, customer, check_amount(opening_deposit))
        self.accounts[number] = account
        customer.accounts.append(account)
        return account

    def transfer(self, from_no, to_no, amount):
        source, target = self.find_account(from_no), self.find_account(to_no)
        if source is target:
            raise ValueError("Cannot transfer to the same account.")
        amount = check_amount(amount)
        target.check_deposit(amount)          # check first so no money is lost
        source.withdraw(amount)
        target.deposit(amount)

    def month_end(self):
        return [(a, *a.month_end()) for a in self.accounts.values()]


