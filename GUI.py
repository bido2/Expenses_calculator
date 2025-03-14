import tkinter as tk
from tkinter import ttk, END
from tkcalendar import DateEntry
from datetime import date, datetime
from sql_actions import insert_data, show_data, delete_transaction, report_query
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


def convert_date(date_str: str) -> str:
    date_obj = datetime.strptime(date_str, '%m/%d/%y')
    return date_obj.strftime('%Y-%m-%d')

def create_gui():
    def new_expense():
        insert_window = tk.Toplevel(root)
        insert_window.title("Podsumowanie wydatków")
        insert_window.geometry("300x400")

        def submit():
            global categories
            categories = load_categories()

            nazwa = nazwa_entry.get()
            kwota = kwota_entry.get()
            selected_date = date_entry.get()
            selected_date = convert_date(selected_date)
            selected_category = category_var.get()

            if selected_category != "Inne" and nazwa:
                for category, keywords in categories.items():
                    if nazwa.lower() in keywords:
                        categories[category] = [item for item in categories[category] if item != nazwa.lower()]


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

        ttk.Label(insert_window, text="Nazwa:").pack(pady=(10, 0))
        nazwa_entry = ttk.Entry(insert_window, width=30)
        nazwa_entry.pack(pady=5)
        nazwa_entry.bind("<KeyRelease>", update_category)

        ttk.Label(insert_window, text="Kwota:").pack(pady=(10, 0))
        kwota_entry = ttk.Entry(insert_window, width=30)
        kwota_entry.pack(pady=5)

        ttk.Label(insert_window, text="Data:").pack(pady=(10, 0))
        date_entry = DateEntry(insert_window, width=27, background="darkblue", foreground="white", borderwidth=2)
        date_entry.set_date(date.today())
        date_entry.pack(pady=5)

        ttk.Label(insert_window, text="Kategoria:").pack(pady=(10, 0))
        category_var = tk.StringVar()
        category_dropdown = ttk.Combobox(insert_window, textvariable=category_var, values=list(categories.keys()),
                                         state="readonly")
        category_dropdown.pack(pady=5)
        category_var.set("Inne")

        submit_button = ttk.Button(insert_window, text="Zatwierdź", command=submit)
        submit_button.pack(pady=10)


    def expenses_summary():

        def delete_selected():
            selected_transaction = tree.focus()
            if not selected_transaction:
                print("Nie wybrano żadnej transakcji")
                return
            transaction_values = tree.item(selected_transaction, "values")
            transaction_id = transaction_values[0]
            delete_transaction(transaction_id)
            tree.delete(selected_transaction)

        summary_window = tk.Toplevel(root)
        summary_window.title("Podsumowanie wydatków")
        summary_window.geometry("500x400")

        ttk.Label(summary_window, text="Lista wydatków", font=("Arial", 14, "bold")).pack(pady=10)

        expenses = show_data()
        columns = ("ID", "Nazwa", "Kwota (PLN)", "Data", "Kategoria")

        tree = ttk.Treeview(summary_window, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c, False))
            tree.column(col, width=100)

        for expense in expenses:
            tree.insert("", tk.END, values=(expense[0], expense[1], expense[2], expense[3], categorize_expense(expense[1])))

        tree.pack(expand=True, fill="both", padx=10, pady=10)

        delete_button = ttk.Button(summary_window, text="Usuń transakcję", command=delete_selected)
        delete_button.pack(pady=5)


    def sort_treeview(tree, col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children("")]

        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)

        for index, (val, child) in enumerate(data):
            tree.move(child, "", index)

        tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))



    def report():
        def show_report():

            min = min_price.get()
            max = max_price.get()

            if min != '' and max != '':
                try:
                    min = int(min)
                    max = int(max)
                except ValueError:
                    print("Bład w danych (kwota)")
                    return
                except Exception as e:
                    print(f"Błąd: {e}")
                    return

            st = start_date.get()
            if st != "":
                st = convert_date(st)

            en = end_date.get()
            if en != "":
                en = convert_date(en)
            cat = category_dropdown.get()

            print(f"{min} {type(min)}, {max} {type(max)}, {st} {type(st)}, {en} {type(en)}, {en} {type(en)}, {cat} {type(cat)}")

            report_window = tk.Toplevel(root)
            report_window.title("Raport")
            report_window.geometry("500x400")

            rows = report_query(min, max, st, en, cat)
            columns = ("ID", "Nazwa", "Kwota (PLN)", "Data", "Kategoria")

            tree = ttk.Treeview(report_window, columns=columns, show="headings", selectmode="browse")

            for col in columns:
                tree.heading(col, text=col, command=lambda c=col: sort_treeview(tree, c, False))
                tree.column(col, width=100)

            for expense in rows:
                tree.insert("", tk.END,
                            values=(expense[0], expense[1], expense[2], expense[3], categorize_expense(expense[1])))

            tree.pack(expand=True, fill="both", padx=10, pady=10)



        report_window = tk.Toplevel(root)
        report_window.title("Raport")
        report_window.geometry("450x250")


        content = ttk.Frame(report_window)
        content.pack(padx=20, pady=20)

        ttk.Label(content, text='Szczegóły raportu', font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4,pady=10)


        ttk.Label(content, text='Kwota').grid(row=1, column=0, pady=10)
        min_price = ttk.Entry(content)
        min_price.grid(row=1, column=1, padx=5)

        ttk.Label(content, text='-').grid(row=1, column=2)

        max_price = ttk.Entry(content)
        max_price.grid(row=1, column=3, padx=5)


        ttk.Label(content, text='Data').grid(row=2, column=0, pady=10)
        start_date = DateEntry(content, width=20, background="darkblue", foreground="white", borderwidth=2)
        start_date.grid(row=2, column=1, padx=5)
        start_date.delete(0, END)

        ttk.Label(content, text='-').grid(row=2, column=2)

        end_date = DateEntry(content, width=20, background="darkblue", foreground="white", borderwidth=2)
        end_date.grid(row=2, column=3, padx=5)
        end_date.delete(0, END)


        categories = load_categories()
        categories_list = list(categories.keys())
        categories_list.insert(0,'Wszystkie')
        ttk.Label(content, text='Kategoria').grid(row=3, column=0, pady=10)
        category_var = tk.StringVar(value=categories_list[0])
        category_dropdown = ttk.Combobox(content, textvariable=category_var, values=categories_list, state="readonly")
        category_dropdown.grid(row=3, column=1, columnspan=3, padx=5)



        ttk.Button(content, text='Generuj', command=show_report).grid(row=5, column=1, columnspan=3, padx=5)



    def show_main_view():
        for widget in root.winfo_children():
            widget.destroy()

        style = ttk.Style()
        style.configure("Big.TButton", padding=(10, 15))

        new_expense_button = ttk.Button(root, text="Nowy wydatek", command=new_expense, width=15, style="Big.TButton")
        new_expense_button.grid(row=0, column=0, padx=20, pady=10)

        expenses_list_button = ttk.Button(root, text="Lista wydatków", command=expenses_summary, width=15,style="Big.TButton")
        expenses_list_button.grid(row=0, column=1, padx=5)

        report_button = ttk.Button(root, text="Raport", command=report, width=15,style="Big.TButton")
        report_button.grid(row=1, column=0, padx=10, pady=10)

    root = tk.Tk()
    root.title("Aplikacja Budżetowa")
    root.geometry("300x150")
    root.configure(bg="#f0f0f0")

    show_main_view()

    root.mainloop()


create_gui()
