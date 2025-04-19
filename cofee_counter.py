import customtkinter as ctk
from datetime import date
import json
import os
import matplotlib.pyplot as plt
from collections import defaultdict
import csv
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



DATA_FILE = "coffee_data.json"

class CoffeeTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("☕ Coffee Budget Tracker")
        self.geometry("230x300")

        self.balance = 0
        self.top_ups = []
        self.coffees = []
        self.default_coffee_price = 5

        self.balance_label = None
        self.default_price_entry = None
        self.topup_entry = None

        self.load_data()
        self.create_widgets()
        self.update_balance()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                self.top_ups = data.get("top_ups", [])
                self.coffees = data.get("coffees", [])
                self.default_coffee_price = data.get("default_coffee_price", 5)

    def save_data(self):
        data = {
            "top_ups": self.top_ups,
            "coffees": self.coffees,
            "default_coffee_price": self.default_coffee_price
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def create_widgets(self):
        # Balance Label
        self.balance_label = ctk.CTkLabel(self, text="Balance: 0.00,- CZK", font=("Arial", 18))
        self.balance_label.pack(pady=10, anchor="w", padx=20)

        # Top-up and Coffee Purchase Buttons
        buy_frame = ctk.CTkFrame(self, fg_color="transparent")
        buy_frame.pack(pady=5, anchor="w", padx=20)
        ctk.CTkButton(buy_frame, text="Buy Coffee ☕", command=self.buy_coffee, width=150, fg_color="green").pack(side="left", padx=(0, 5))
        ctk.CTkButton(buy_frame, text="❌", width=30, command=self.undo_coffee, fg_color="red").pack(side="left")

        # Top-up Entry and Buttons
        self.topup_entry = ctk.CTkEntry(self, placeholder_text="Top-up amount", width=150)  # Adjusted input width
        self.topup_entry.pack(pady=2, anchor="w", padx=20)
        topup_frame = ctk.CTkFrame(self, fg_color="transparent")
        topup_frame.pack(pady=5, anchor="w", padx=20)
        ctk.CTkButton(topup_frame, text="Add Top-up", command=self.add_topup, width=150).pack(side="left", padx=(0, 5))
        ctk.CTkButton(topup_frame, text="❌", width=30, command=self.undo_topup, fg_color="red").pack(side="left")

        # Default Coffee Price Entry and Buttons
        self.default_price_entry = ctk.CTkEntry(self, placeholder_text="Set coffee price", width=150)  # Adjusted input width
        self.default_price_entry.pack(pady=2, anchor="w", padx=20)
        ctk.CTkButton(self, text="Update Coffee Price", command=self.set_default_price, width=150).pack(pady=5, anchor="w", padx=20)

        # Statistics and History Buttons
        ctk.CTkButton(self, text="📊 Show Stats", command=self.show_stats_window, width=150).pack(pady=10, anchor="w", padx=20)


    def show_stats_window(self):
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Statistics")
        stats_window.geometry("300x300")

        ctk.CTkLabel(stats_window, text="Statistics & History", font=("Arial", 16)).pack(pady=10)

        ctk.CTkButton(stats_window, text="📜 View Top-Up History", command=self.show_topup_history).pack(pady=5)
        ctk.CTkButton(stats_window, text="☕ View Coffee History", command=self.show_coffee_history).pack(pady=5)
        ctk.CTkButton(stats_window, text="📁 Export History to CSV", command=self.export_to_csv).pack(pady=5)
        ctk.CTkButton(stats_window, text="📊 Show Monthly Summary", command=self.show_monthly_summary).pack(pady=5)

    def update_balance(self):
        total_topups = sum(t['amount'] for t in self.top_ups)
        total_spent = sum(c['price'] for c in self.coffees)
        self.balance = total_topups - total_spent

        balance_text = f"Balance: {self.balance:.2f},-CZK"
        if self.balance < 10:
            self.balance_label.configure(text=f"⚠️ {balance_text}", text_color="red")
        else:
            self.balance_label.configure(text=balance_text, text_color="white")

        self.save_data()

    def add_topup(self):
        try:
            amount = float(self.topup_entry.get())
            self.top_ups.append({"amount": amount, "date": str(date.today())})
            self.topup_entry.delete(0, 'end')
            self.update_balance()
        except ValueError:
            print("Invalid top-up value")

    def undo_topup(self):
        if self.top_ups:
            self.top_ups.pop()
            self.update_balance()

    def set_default_price(self):
        try:
            price = float(self.default_price_entry.get())
            self.default_coffee_price = price
            self.default_price_entry.delete(0, 'end')
            self.save_data()
        except ValueError:
            print("Invalid coffee price")

    def buy_coffee(self):
        self.coffees.append({"price": self.default_coffee_price, "date": str(date.today())})
        self.update_balance()

    def undo_coffee(self):
        if self.coffees:
            self.coffees.pop()
            self.update_balance()

    def show_topup_history(self):
        history_window = ctk.CTkToplevel(self)
        history_window.title("Top-Up History")
        history_window.geometry("300x400")

        ctk.CTkLabel(history_window, text="Top-Up History", font=("Arial", 16)).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(history_window, width=250, height=300)
        scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        if not self.top_ups:
            ctk.CTkLabel(scroll_frame, text="No top-ups yet.").pack(pady=5)
        else:
            for topup in reversed(self.top_ups):
                msg = f"{topup['date']}: {topup['amount']:.2f},- CZK"
                ctk.CTkLabel(scroll_frame, text=msg, anchor="w").pack(fill="x", padx=5, pady=2)

    def show_coffee_history(self):
        history_window = ctk.CTkToplevel(self)
        history_window.title("Coffee Purchase History")
        history_window.geometry("300x400")

        ctk.CTkLabel(history_window, text="Coffee Purchase History", font=("Arial", 16)).pack(pady=10)

        scroll_frame = ctk.CTkScrollableFrame(history_window, width=250, height=300)
        scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)

        if not self.coffees:
            ctk.CTkLabel(scroll_frame, text="No coffees bought yet.").pack(pady=5)
        else:
            for coffee in reversed(self.coffees):
                msg = f"{coffee['date']}: {coffee['price']:.2f},- CZK"
                ctk.CTkLabel(scroll_frame, text=msg, anchor="w").pack(fill="x", padx=5, pady=2)

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
            title="Save CSV Export"
        )
        if not file_path:
            return

        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Type", "Amount", "Date"])

                for topup in self.top_ups:
                    writer.writerow(["Top-Up", f"{topup['amount']:.2f}", topup['date']])
                for coffee in self.coffees:
                    writer.writerow(["Coffee", f"{coffee['price']:.2f}", coffee['date']])
        except Exception as e:
            print(f"Error exporting CSV: {e}")

    def show_monthly_summary(self):
        monthly_totals = defaultdict(float)
        for coffee in self.coffees:
            month = coffee['date'][:7]  # YYYY-MM
            monthly_totals[month] += coffee['price']

        if not monthly_totals:
            print("No coffee data to plot.")
            return

        months = sorted(monthly_totals)
        totals = [monthly_totals[m] for m in months]

        chart_window = ctk.CTkToplevel(self)
        chart_window.title("📊 Monthly Coffee Spending")
        chart_window.geometry("500x350")

        fig, ax = plt.subplots(figsize=(6, 3))
        bars = ax.bar(months, totals, color='saddlebrown')
        ax.set_title("Monthly Coffee Spending")
        ax.set_ylabel("CZK")
        ax.set_xlabel("Month")
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()

        for bar, total in zip(bars, totals):
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.3, f"{yval:.2f}", ha='center', va='bottom', fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)



if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = CoffeeTrackerApp()
    app.mainloop()
