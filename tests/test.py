# from source.customWidgets import *
import customtkinter
from tkinter import *
from tkinter.ttk import Notebook, Style

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

root_tk = customtkinter.CTk()  # create CTk window like the Tk window
root_tk.geometry("400x240")

style = Style()
style.layout('TNotebook.Tab', [])  # turn off tabs
note = Notebook(root_tk)

# frame = customtkinter.CTkFrame(master=note,
#                                width=200,
#                                height=200,
#                                corner_radius=10)
# button = customtkinter.CTkButton(master=frame, command=lambda: note.select(1))
# button.place(relx=0.5, rely=0.5, anchor=CENTER)

# cbutton = MenuButton(frame, 'hello', 'Helvetica 13 bold',
#                      lambda: print('test'))
# cbutton.pack()

# note.add(frame)

# frame2 = customtkinter.CTkFrame(master=note,
#                                 width=200,
#                                 height=200,
#                                 corner_radius=10)
# button2 = customtkinter.CTkButton(
#     master=frame2, command=lambda: note.select(0))
# button2.pack()
# note.add(frame2)

# note.pack(expand=1, fill='both', padx=5, pady=5)


root_tk.mainloop()
