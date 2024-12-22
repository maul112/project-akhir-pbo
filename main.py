import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QFont
from database import Database
from observer import Subject

class BudgetManager(QMainWindow, Subject):
    def __init__(self):
        super().__init__()
        Subject.__init__(self)
        self.setWindowTitle("Budget Manager")
        self.setGeometry(100, 100, 700, 400)  # Ukuran lebih besar

        self.db = Database().get_connection()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Font untuk memperbesar teks
        font = QFont("Arial", 12)

        # Input Area
        input_layout = QVBoxLayout()
        title_input_layout = QHBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setFont(font)
        self.title_input.setPlaceholderText("Enter title (e.g., Salary, Rent)")

        self.amount_input = QLineEdit()
        self.amount_input.setFont(font)
        self.amount_input.setPlaceholderText("Enter amount (e.g., 1000)")

        self.add_income_btn = QPushButton("Add Income")
        self.add_income_btn.setFont(font)
        self.add_income_btn.clicked.connect(lambda: self.add_transaction("Income"))

        self.add_expense_btn = QPushButton("Add Expense")
        self.add_expense_btn.setFont(font)
        self.add_expense_btn.clicked.connect(lambda: self.add_transaction("Expense"))

        title_input_layout.addWidget(self.title_input)
        title_input_layout.addWidget(self.amount_input)
        input_layout.addLayout(title_input_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_income_btn)
        button_layout.addWidget(self.add_expense_btn)
        input_layout.addLayout(button_layout)

        main_layout.addLayout(input_layout)

        # Transaction Table
        self.table = QTableWidget(0, 4)  # Tambahkan kolom untuk tombol Delete
        self.table.setFont(font)
        self.table.setHorizontalHeaderLabels(["Title", "Type", "Amount", "Action"])
        main_layout.addWidget(self.table)

        # Total Balance
        self.total_label = QLabel("Total Balance: 0")
        self.total_label.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(self.total_label)

        # Container Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Attach Observer
        self.attach(self)

        # Load Initial Data
        self.load_transactions()

    def add_transaction(self, t_type):
        title = self.title_input.text().strip()
        amount_text = self.amount_input.text().strip()

        if not title:
            self.title_input.setPlaceholderText("Title cannot be empty!")
            return

        try:
            amount = float(amount_text)
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO transactions (title, type, amount) VALUES (?, ?, ?)",
                (title, t_type, amount)
            )
            self.db.commit()
            self.title_input.clear()
            self.amount_input.clear()
            self.notify()  # Notify observers
        except ValueError:
            self.amount_input.setText("Invalid amount")

    def load_transactions(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT id, title, type, amount FROM transactions")
        transactions = cursor.fetchall()

        self.table.setRowCount(0)  # Clear table
        for row_idx, (transaction_id, title, t_type, amount) in enumerate(transactions):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(title))
            self.table.setItem(row_idx, 1, QTableWidgetItem(t_type))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{amount:.2f}"))

            # Add Delete Button
            delete_btn = QPushButton("Delete")
            delete_btn.setFont(QFont("Arial", 10))
            delete_btn.clicked.connect(lambda _, tid=transaction_id: self.delete_transaction(tid))
            self.table.setCellWidget(row_idx, 3, delete_btn)

        self.update_total()

    def delete_transaction(self, transaction_id):
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        self.db.commit()
        self.notify()  # Notify observers

    def update_total(self):
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END) -
                SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END)
            FROM transactions
        """)
        total_balance = cursor.fetchone()[0] or 0
        self.total_label.setText(f"Total Balance: {total_balance:.2f}")

    def update(self):
        self.load_transactions()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BudgetManager()
    window.show()
    sys.exit(app.exec_())