import tkinter as tk
from tkinter import messagebox

from auth import authenticate_user


def attempt_login(email_entry, password_entry, root):

    email = email_entry.get()
    password = password_entry.get()

    user = authenticate_user(
        email,
        password
    )

    if user is None:
        messagebox.showerror(
            "Login Failed",
            "The email or password is incorrect, or the account is locked"
        )

        return

    if user.must_change:
        messagebox.showwarning(
            "Password Change Required",
            "You must change your temporary password before continuing"
        )

        # replace this with the change password window once created + ui etc. has been enforced
        return

    root.destroy()

    if user.role == "Admin":
        from ui.admin import open_admin_page
        open_admin_page(user)

    elif user.role == "Manager":
        from ui.manager import open_manager_page
        open_manager_page(user)

    elif user.role == "Employee":
        from ui.employee import open_employee_page
        open_employee_page(user)

    else:
        messagebox.showerror(
            "Access Denied",
            "The account does not have a recognised role"
        )


def open_login_page():

    root = tk.Tk()
    root.title("Lock IT Down - Login")
    root.geometry("1000x650")

    heading = tk.Label(
        root,
        text="Lock IT Down",
        font=("Arial", 24, "bold")
    )
    heading.pack(pady=30)

    email_label = tk.Label(
        root,
        text="Email"
    )
    email_label.pack()

    email_entry = tk.Entry(
        root,
        width=40
    )
    email_entry.pack(pady=5)

    password_label = tk.Label(
        root,
        text="Password"
    )
    password_label.pack()

    password_entry = tk.Entry(
        root,
        width=40,
        show="*"
    )
    password_entry.pack(pady=5)

    login_button = tk.Button(
        root,
        text="Login",
        command=lambda: attempt_login(
            email_entry,
            password_entry,
            root
        )
    )
    login_button.pack(pady=20)

    root.mainloop()
