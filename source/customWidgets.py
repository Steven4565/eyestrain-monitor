from tkinter import *


def MenuButton(root, text, font, onClick, color=['#23a8f2', '#1b85bf']):
    label = Label(root, height=2, text=text, font=(font))
    label.config(foreground=color[0], background='#2a2d2e')

    # Bind the Enter and Leave Events to the Button
    label.bind('<ButtonRelease-1>', lambda e: onClick())
    label.bind('<Leave>', lambda e: label.config(foreground=color[0]))
    label.bind('<Enter>', lambda e: label.config(foreground=color[1]))

    return label
