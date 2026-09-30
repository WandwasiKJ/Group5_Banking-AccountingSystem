"""-------GROUP 5 BANKING AND ACCOUNT MANAGEMENT SYSTEM-------"""
class Customer:
    def __init__(self, customer_id, name, phone):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.accounts = []

    def add_account(self, account):
        self.accounts.append(account)

    def get_accounts(self):
        return self.accounts


from abc import ABC, abstractmethod

class BankAccount(ABC):
    def __init__(self,account_number, customer):
        self.account_number = account_number
        self.customer = customer
        self.balance = 0.0

    @property    #turns a method into a “read-only attribute” from the caller’s point of view.
    def balance(self):
        return self.balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self.balance += amount 

    @abstractmethod
    def withdrawal(self, amount):
        pass

    @abstractmethod
    def calculate_interest(self,months=1):
        pass

# Use a property to allow users to see their account balance without directly accessing the attribute.
        
    @property
    def balance(self):
        return self.balance
    """--The actual balance remains controlled by the class hence encapsulation and controlled access.."""        

 #   Add transaction  class with a history

class Transaction:

    def __init__(self, transaction_type, amount, description):
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.transactions = []
        self.transactions.append(
            Transaction("DEPOSIT", amount, "Cash deposit"))
    
    def __str__(self):
        return f"{self.transaction_type}: {self.amount} - {self.description}"     

            


class SavingsAccount(BankAccount): #inherits common functionality from BankAccount.

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if amount > self.balance:
            raise ValueError("Insufficient funds.")

    def calculate_interest(self, months=1):
        interest_rate = 0.05
        return self.balance * interest_rate * months/12  # Simple interest calculation for the given number of months.
    
    def apply_interest(self, months=1):
        interest = self.calculate_interest(months)
        self.balance += interest
        
        return interest

class CurrentAccount(BankAccount): #inherits common functionality from BankAccount.

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if amount > self.balance:
            raise ValueError("Insufficient funds.")
            # current account may allow an overdraft
            # depending on the rules you define

    def calculate_interest(self, months=1):
        return 0.0  # Current accounts typically do not earn interest.kli  