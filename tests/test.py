from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image

IMAGE_PATH = './assets/images/blink.png'


class Overlay:
    root = Toplevel()

    def __init__(self):

        self.root.overrideredirect(True)
        self.root.geometry("100x60+5+5")
        self.root.lift()
        self.root.wm_attributes("-topmost", True)

        img = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((100, 60)))
        image_panel = Label(self.root, image=img,
                            highlightthickness=0, borderwidth=0)
        image_panel.grid(sticky="news")
        image_panel.configure(image=img)
        image_panel.image = img

        self.root.bind("<<CloseOverlay>>", self.close)
        self.root.bind("<<HideOverlay>>", self.hide)
        self.root.bind("<<ShowOverlay>>", self.show)

    def show(self, e):
        self.root.deiconify()

    def hide(self, e):
        self.root.withdraw()

    def close(self, e):
        sys.exit()


overlay = Overlay()


def close_overlay():
    overlay.root.event_generate("<<CloseOverlay>>")


def show_overlay():
    overlay.root.event_generate("<<ShowOverlay>>")


def hide_overlay():
    overlay.root.event_generate("<<HideOverlay>>")


root_tk = CTk()
CTkButton(master=root_tk, text="Close", command=lambda: close_overlay()).grid()
CTkButton(master=root_tk, text="Hide", command=lambda: hide_overlay()).grid()
CTkButton(master=root_tk, text="Show", command=lambda: show_overlay()).grid()


def on_close():
    root_tk.destroy()
    overlay.root.destroy()


root_tk.protocol("WM_DELETE_WINDOW", on_close)

root_tk.mainloop()
