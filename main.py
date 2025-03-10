from sql_actions import *
from GUI import create_gui

if __name__ == '__main__':
    db_create()
    show_data()
    window = create_gui()
    window.mainloop()