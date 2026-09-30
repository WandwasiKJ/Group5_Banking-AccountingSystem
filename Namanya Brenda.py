class FixedDepositAccount(BankAccount):

    def __init__(self, account_number, customer):
        super().__init__(account_number, customer) #this allows the class to communicate with the subclass

        self.account_type = "Fixed Deposit Account"

        self.interest_rate = 0.10

        # Fixed deposit cannot be withdrawn before maturity.
        self.is_matured = False

    def withdraw(self, amount):

        if not self.is_matured:
            raise ValueError(
                "Withdrawal denied. "
                "Fixed deposit has not matured yet."
            )

        if amount <= 0:
            raise ValueError(
                "Withdrawal amount must be greater than zero."
            )

        if amount > self.balance:
            raise ValueError(
                "Withdrawal denied. Insufficient balance."
            )

        self._balance = self._balance - amount

        transaction = Transaction(
            "WITHDRAWAL",
            amount,
            "Fixed deposit withdrawal after maturity"
        )

        self.transactions.append(transaction)

        print(
            f"Withdrawal successful. "
            f"New balance: UGX {self.balance:,.2f}"
        )

  
    # calculating interest()
    def calculate_interest(self):

        interest = self.balance * self.interest_rate

        return interest


    def calculate_charge(self):

        # Fixed deposits have no transaction charge
        return 0

