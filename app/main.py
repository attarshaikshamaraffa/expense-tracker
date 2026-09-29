import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

import db

CATEGORIES = ["Food", "Transport", "Rent", "Shopping", "Bills", "Entertainment", "Health", "Other"]


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        root.title("Expense Tracker")
        root.geometry("780x520")
        root.minsize(700, 480)

        self.month_var = tk.StringVar(value=datetime.now().strftime("%Y-%m"))
        self.filter_category_var = tk.StringVar(value="All")

        self._build_form()
        self._build_filters()
        self._build_table()
        self._build_summary()
        self.refresh()

    def _build_form(self):
        frame = ttk.LabelFrame(self.root, text="Add Expense")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Date (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(frame, width=13)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Category").grid(row=0, column=2, padx=5)
        self.category_box = ttk.Combobox(frame, values=CATEGORIES, width=13, state="readonly")
        self.category_box.current(0)
        self.category_box.grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Amount").grid(row=0, column=4, padx=5)
        self.amount_entry = ttk.Entry(frame, width=10)
        self.amount_entry.grid(row=0, column=5, padx=5)

        ttk.Label(frame, text="Note").grid(row=0, column=6, padx=5)
        self.note_entry = ttk.Entry(frame, width=18)
        self.note_entry.grid(row=0, column=7, padx=5)

        ttk.Button(frame, text="Add", command=self.add_expense).grid(row=0, column=8, padx=10)

    def _build_filters(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10)

        ttk.Label(frame, text="Month (YYYY-MM):").pack(side="left")
        ttk.Entry(frame, textvariable=self.month_var, width=10).pack(side="left", padx=5)

        ttk.Label(frame, text="Category:").pack(side="left", padx=(15, 0))
        self.filter_box = ttk.Combobox(frame, textvariable=self.filter_category_var,
                                        values=["All"] + CATEGORIES, width=14, state="readonly")
        self.filter_box.pack(side="left", padx=5)

        ttk.Button(frame, text="Apply Filter", command=self.refresh).pack(side="left", padx=10)
        ttk.Button(frame, text="Clear Filter", command=self.clear_filter).pack(side="left")

    def _build_table(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "date", "category", "amount", "note")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        widths = {"id": 40, "date": 100, "category": 110, "amount": 90, "note": 250}
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=widths[col], anchor="w")
        self.tree.column("id", anchor="center")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(self.root, text="Delete Selected", command=self.delete_selected).pack(pady=(0, 10))

    def _build_summary(self):
        frame = ttk.LabelFrame(self.root, text="Summary")
        frame.pack(fill="x", padx=10, pady=(0, 10))

        self.total_label = ttk.Label(frame, text="Total: 0.00", font=("Segoe UI", 11, "bold"))
        self.total_label.pack(side="left", padx=10, pady=5)

        self.breakdown_label = ttk.Label(frame, text="")
        self.breakdown_label.pack(side="left", padx=10, pady=5)

    def add_expense(self):
        date_str = self.date_entry.get().strip()
        category = self.category_box.get()
        amount_str = self.amount_entry.get().strip()
        note = self.note_entry.get().strip()

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Use the format YYYY-MM-DD, e.g. 2026-09-29")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid amount", "Amount must be a positive number")
            return

        db.add_expense(date_str, category, amount, note)
        self.amount_entry.delete(0, "end")
        self.note_entry.delete(0, "end")
        self.refresh()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select a row to delete first")
            return
        if not messagebox.askyesno("Confirm", "Delete the selected expense(s)?"):
            return
        for item in selected:
            expense_id = self.tree.item(item)["values"][0]
            db.delete_expense(expense_id)
        self.refresh()

    def clear_filter(self):
        self.month_var.set("")
        self.filter_category_var.set("All")
        self.refresh()

    def refresh(self):
        month = self.month_var.get().strip() or None
        category = self.filter_category_var.get()

        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in db.get_expenses(month=month, category=category):
            self.tree.insert("", "end", values=r)

        self.total_label.config(text=f"Total: {db.get_total(month=month):.2f}")

        cat_totals = db.get_category_totals(month=month)
        breakdown = "  |  ".join(f"{c}: {t:.0f}" for c, t in cat_totals[:5])
        self.breakdown_label.config(text=breakdown)


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()