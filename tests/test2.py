# Import required libraries
from tkinter import *
# Create an instance of tkinter frame
win = Tk()


def on_release(e):
    print('test')


def on_leave(e):
    label.config(foreground="#23a8f2")


def on_enter(e):
    label.config(foreground='#1b85bf')


# Create a Button
label = Label(win, text="Click Me", font=('Helvetica 13 bold'))
label.config(foreground="#23a8f2")
label.pack(pady=20)

# Bind the Enter and Leave Events to the Button
label.bind('<ButtonRelease-1>', on_release)
label.bind('<Leave>', on_leave)
label.bind('<Enter>', on_enter)
