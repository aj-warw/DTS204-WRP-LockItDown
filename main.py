import tkinter as tk
from db import initialise_database



def main(): # create main app window
    initialise_database() # creates database when app is run
    root = tk.Tk()
    root.title("Lock IT Down")
    root.geometry("1000x650")

    heading = tk.Label( # display a heading inside the root window
        root,
        text="Lock IT Down Temp Page"
    )

    heading.pack(pady=30) # add padding on y axis with pady 

    root.mainloop() # run tkinter event loop


if __name__ == "__main__": # just to ensure that main() only executes when main is run, not when main is imported anywhere.
    main()