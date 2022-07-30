from customtkinter import *


def populate_activity_page(frame):
	for thing in range(20):
		CTkButton(frame, text=f'Button {thing} Yo!').grid(
							row=thing, column=0, pady=10, padx=10)
