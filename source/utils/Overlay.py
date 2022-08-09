from tkinter import Tk, Label, Toplevel
from PIL import Image, ImageTk
import sys


class Overlay:
    window: Toplevel
    def __init__(self, master,blink_image_dir, break_image_dir):
        self.window = Toplevel(master)
        self.window.overrideredirect(True)
        self.window.geometry("100x60+5+5")
        self.window.lift()
        self.window.wm_attributes("-topmost", True)

        self.blink_image = ImageTk.PhotoImage(Image.open(
            blink_image_dir).resize((100, 60)))
        self.break_image = ImageTk.PhotoImage(Image.open(
            break_image_dir).resize((100, 60)))

        self.image_panel = Label(
            self.window, highlightthickness=0, borderwidth=0)
        self.image_panel.grid(sticky="news")

        # self.window.withdraw()

    def remind_blink(self):
        self.remind(self.blink_image)

    def remind_break(self):
        self.remind(self.break_image)

    def remind(self, image):
        self.set_image(image)
        self.window.deiconify()
        self.window.after(5000, lambda: self.window.withdraw())

    def set_image(self, image):
        self.image_panel.configure(image=image)
        self.image_panel.image = image

    def close(self):
        self.window.destroy()

IMAGE_PATH = './assets/images/blink.png'


# class Overlay:
#     window: Toplevel

#     def __init__(self, master):
#         self.window = Toplevel(master=master)

#         self.window.overrideredirect(True)
#         self.window.geometry("100x60+5+5")
#         self.window.lift()
#         self.window.wm_attributes("-topmost", True)

#         img = ImageTk.PhotoImage(Image.open(IMAGE_PATH).resize((100, 60)))
#         image_panel = Label(self.window, image=img,
#                             highlightthickness=0, borderwidth=0)
#         image_panel.grid(sticky="news")
#         image_panel.configure(image=img)
#         image_panel.image = img

#         self.window.bind("<<CloseOverlay>>", self.close)
#         self.window.bind("<<HideOverlay>>", self.hide)
#         self.window.bind("<<ShowOverlay>>", self.show)

#     def show(self, e):
#         self.window.deiconify()

#     def hide(self, e):
#         self.window.withdraw()

#     def close(self, e):
#         sys.exit()
