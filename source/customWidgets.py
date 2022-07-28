from tkinter import *

def MenuButtonTemplate(root, font, color=['#23a8f2', '#1b85bf', "#212325", "#43474b"]):
    return lambda text, onClick, selected=None: MenuButton(root, text, font, onClick, color, selected)


def MenuButton(root, text, font, onClick, color=['#23a8f2', '#1b85bf'], selected=False):
    label = Label(root, pady=10, padx=60, text=text, font=(font))
    isSelected = selected
    label.config(foreground=color[0], background='#212325')

    def onSelect(e):
        nonlocal isSelected
        isSelected = True
        label.config(foreground=color[1], background=color[3])
    def onDeSelect(e):
        nonlocal isSelected
        isSelected = False
        label.config(foreground=color[0], background=color[2])

    # On creation
    if selected:
        onSelect(None)


    # Bind the Enter and Leave Events to the Button
    label.bind('<ButtonRelease-1>', lambda e: onClick())
    label.bind('<Leave>', lambda e: not isSelected and label.config(foreground=color[0], background=color[2]))
    label.bind('<Enter>', lambda e: label.config(foreground=color[1], background=color[3]))

    label.bind("<<MenuSelect>>", onSelect)
    label.bind("<<MenuDeSelect>>", onDeSelect)

    return label
