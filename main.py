import tkinter as tk

def main(): # create main app window
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