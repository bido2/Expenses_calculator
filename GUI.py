import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date, datetime
from sql_actions import insert_data, show_data
import json

def save_categories(categories):
    with open('categories.json', 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=4)

def load_categories():
    with open('categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
        return categories


def categorize_expense(expense_name):
    global categories
    categories = load_categories()

    for category, keywords in categories.items():
        if any(keyword in expense_name.lower() for keyword in keywords):
            return category

    return "Inne"


def update_category(event):
    selected_name = nazwa_entry.get()
    category = categorize_expense(selected_name)
    category_var.set(category)


def create_gui():
    def show_form():
        for widget in root.winfo_children():
            widget.destroy()

        def convert_date(date_str: str) -> str:
            date_obj = datetime.strptime(date_str, '%m/%d/%y')
            return date_obj.strftime('%Y-%m-%d')

        def submit():
            global categories
            categories = load_categories()

            nazwa = nazwa_entry.get()
            kwota = kwota_entry.get()
            selected_date = date_entry.get()
            selected_date = convert_date(selected_date)
            selected_category = category_var.get()

            if selected_category != "Inne" and nazwa:
                # Na początku usuwamy nazwa z wszystkich kategorii, jeśli się w nich znajduje
                for category, keywords in categories.items():
                    if nazwa.lower() in keywords:
                        categories[category] = [item for item in categories[category] if item != nazwa.lower()]

                # Teraz dodajemy nazwa do odpowiedniej kategorii
                categories[selected_category].append(nazwa.lower())

            nazwa_entry.delete(0, tk.END)
            kwota_entry.delete(0, tk.END)
            date_entry.set_date(date.today())
            category_var.set("Inne")

            insert_data(nazwa, kwota, selected_date, selected_category)
            print(categories)
            save_categories(categories)
            show_main_view()

        global nazwa_entry, kwota_entry, date_entry, category_var, categories
        categories = load_categories()

        ttk.Label(root, text="Nazwa:").pack(pady=(10, 0))
        nazwa_entry = ttk.Entry(root, width=30)
        nazwa_entry.pack(pady=5)
        nazwa_entry.bind("<KeyRelease>", update_category)

        ttk.Label(root, text="Kwota:").pack(pady=(10, 0))
        kwota_entry = ttk.Entry(root, width=30)
        kwota_entry.pack(pady=5)

        ttk.Label(root, text="Data:").pack(pady=(10, 0))
        date_entry = DateEntry(root, width=27, background="darkblue", foreground="white", borderwidth=2)
        date_entry.set_date(date.today())
        date_entry.pack(pady=5)

        ttk.Label(root, text="Kategoria:").pack(pady=(10, 0))
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(root, textvariable=category_var, values=list(categories.keys()),
                                         state="readonly")
        category_dropdown.pack(pady=5)
        category_var.set("Inne")

        submit_button = ttk.Button(root, text="Zatwierdź", command=submit)
        submit_button.pack(pady=10)

    import tkinter as tk
    from tkinter import ttk

    def show_summary():
        summary_window = tk.Toplevel(root)
        summary_window.title("Podsumowanie wydatków")
        summary_window.geometry("400x300")

        ttk.Label(summary_window, text="Lista wydatków", font=("Arial", 14, "bold")).pack(pady=10)

        expenses = show_data()
        columns = ("Nazwa", "Kwota (PLN)", "Data", "Kategoria")

        tree = ttk.Treeview(summary_window, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c, False))

        tree.column("Nazwa", width=100)
        tree.column("Kwota (PLN)", width=80)
        tree.column("Data", width=100)
        tree.column("Kategoria", width=100)

        for expense in expenses:
            tree.insert("", tk.END, values=(expense[1], expense[2], expense[3], categorize_expense(expense[1])))

        tree.pack(expand=True, fill="both", padx=10, pady=10)

    def sort_treeview(tree, col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children("")]

        # Spróbuj zamienić wartości na liczby, jeśli to możliwe (np. dla kwot)
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)

        for index, (val, child) in enumerate(data):
            tree.move(child, "", index)

        tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))

    def show_main_view():
        for widget in root.winfo_children():
            widget.destroy()

        new_expense_button = ttk.Button(root, text="Nowy wydatek", command=show_form)
        new_expense_button.pack(side=tk.LEFT, padx=5, pady=20)

        expenses_list = ttk.Button(root, text="Lista wydatków", command=show_summary)
        expenses_list.pack(side=tk.RIGHT, padx=5, pady=20)

    root = tk.Tk()
    root.title("Aplikacja Budżetowa")
    root.geometry("300x400")
    root.configure(bg="#f0f0f0")

    show_main_view()

    root.mainloop()



create_gui()
