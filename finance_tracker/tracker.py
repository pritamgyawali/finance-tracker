from cryptography.fernet import Fernet
import os
import json

class FinanceManager:
    def __init__(self):
        self.fernet = self.load_key()
        self.data = self.read_data()

    def load_key(self):
        """Load or generate a new encryption key."""
        if not os.path.exists("secret.key"):
            key = Fernet.generate_key()
            with open("secret.key", "wb") as key_file:
                key_file.write(key)
            print("Generated new encryption key.")
        else:
            with open("secret.key", "rb") as key_file:
                key = key_file.read()
        return Fernet(key)

    def read_data(self):
        """Read and decrypt data from the file."""
        if not os.path.exists("data.txt"):
            return {}
        try:
            with open("data.txt", "rb") as file:
                encrypted_data = file.read()
            if not encrypted_data:
                return {}
            decrypted_data = self.fernet.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
        except Exception as e:
            print(f"Error reading data: {e}")
            return {}

    def write_data(self):
        """Encrypt and write data to the file."""
        try:
            encrypted_data = self.fernet.encrypt(json.dumps(self.data).encode())
            with open("data.txt", "wb") as file:
                file.write(encrypted_data)
        except Exception as e:
            print(f"Error writing data: {e}")

    def initialize_files(self):
        """Initialize files with default data if they do not exist."""
        if not os.path.exists("data.txt"):
            with open("data.txt", "wb") as file:
                file.write(b'{}')  # Write an empty JSON object
            print("Created new data file.")

        # Ensure initial balances are set
        if 'balances' not in self.data:
            self.data['balances'] = {'B': 0.0, 'D': 0.0, 'P': 0.0}
            self.write_data()
            print("Initialized balances for B, D, and P.")

    def print_balance(self):
        """Print the balance overview for all account types."""
        print("\nBalance Overview:")
        for key, value in self.data.get('balances', {}).items():
            print(f"{key}: ${value:.2f}")

    def update_balance(self, account, amount):
        """Update the balance for a given account."""
        if account not in self.data.get('balances', {}):
            self.data['balances'][account] = 0
        self.data['balances'][account] += amount
        print(f"Updated {account} balance: ${self.data['balances'][account]:.2f}")
    def add_transaction(self, transaction_type, amount, brief_info, personal_note, account_type):
        """Add a transaction to the records."""
        if 'transactions' not in self.data:
            self.data['transactions'] = {'spent': [], 'received': []}

        transaction = {
            'amount': amount,
            'brief_info': brief_info,
            'personal_note': personal_note,
            'account_type': account_type
        }
        
        if transaction_type == 'spent':
            self.data['transactions']['spent'].append(transaction)
            self.update_balance(account_type, -amount)
        elif transaction_type == 'received':
            self.data['transactions']['received'].append(transaction)
            self.update_balance(account_type, amount)
        
        print(f"Transaction added: {transaction_type} ${amount:.2f} to {account_type}")

    def transfer_money(self, from_account, to_account, amount):
        """Transfer money between accounts."""
        if from_account not in self.data.get('balances', {}) or to_account not in self.data.get('balances', {}):
            print("One or both account types are invalid.")
            print(f"Available accounts: {list(self.data.get('balances', {}).keys())}")
            return

        if self.data['balances'][from_account] < amount:
            print("Insufficient funds.")
            return

        self.data['balances'][from_account] -= amount
        self.data['balances'][to_account] += amount

        transaction_info = {
            'amount': amount,
            'brief_info': f"Transfer from {from_account} to {to_account}",
            'personal_note': "Transfer",
            'account_type': from_account
        }

        if 'transactions' not in self.data:
            self.data['transactions'] = {'spent': [], 'received': []}
        
        self.data['transactions']['spent'].append(transaction_info)
        print(f"Transferred ${amount:.2f} from {from_account} to {to_account}")

    def view_transaction_history(self):
        """View transaction history for spent and received transactions."""
        if 'transactions' not in self.data:
            print("No transactions recorded.")
            return
        
        print("\nTransaction History:")
        
        print("\nSpent Transactions:")
        spent_transactions = self.data['transactions'].get('spent', [])
        if not spent_transactions:
            print("No spent transactions found.")
        for transaction in spent_transactions:
            print(f"Amount: ${transaction['amount']:.2f}, Info: {transaction['brief_info']}, Note: {transaction['personal_note']}, Account: {transaction['account_type']}")
        
        print("\nReceived Transactions:")
        received_transactions = self.data['transactions'].get('received', [])
        if not received_transactions:
            print("No received transactions found.")
        for transaction in received_transactions:
            print(f"Amount: ${transaction['amount']:.2f}, Info: {transaction['brief_info']}, Note: {transaction['personal_note']}, Account: {transaction['account_type']}")

def main():
    """Main function to handle user interaction."""
    finance_manager = FinanceManager()
    finance_manager.initialize_files()

    while True:
        print("\nOptions:")
        print("1. Print balance")
        print("2. Add transaction")
        print("3. Transfer money")
        print("4. View transaction history")
        print("5. Exit")
        choice = input("Enter choice: ")
        
        if choice == '1':
            finance_manager.print_balance()
        elif choice == '2':
            transaction_type = input("Enter transaction type (spent/received): ").strip()
            amount = float(input("Enter amount: "))
            brief_info = input("Enter brief info: ").strip()
            personal_note = input("Enter personal note: ").strip()
            account_type = input("Enter account type (P/B/D): ").strip()
            finance_manager.add_transaction(transaction_type, amount, brief_info, personal_note, account_type)
        elif choice == '3':
            print("Transfer Options:")
            print("1. Bank to Digital Wallet (B to D)")
            print("2. Bank to Physical Cash (B to P)")
            print("3. Physical Cash or Digital Wallet to Bank (P or D to B)")
            transfer_option = input("Enter transfer option: ").strip()

            if transfer_option == '1':
                amount = float(input("Enter amount to transfer: "))
                finance_manager.transfer_money('B', 'D', amount)
            elif transfer_option == '2':
                amount = float(input("Enter amount to withdraw: "))
                finance_manager.transfer_money('B', 'P', amount)
            elif transfer_option == '3':
                from_account = input("Enter source account (P/D): ").strip()
                amount = float(input("Enter amount to transfer: "))
                finance_manager.transfer_money(from_account, 'B', amount)
            else:
                print("Invalid transfer option.")
        elif choice == '4':
            finance_manager.view_transaction_history()
        elif choice == '5':
            finance_manager.write_data()
            print("Data saved. Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()