from tkinter import Tk, Label, Toplevel
from PIL import Image, ImageTk
import sys


# class Overlay:
#     root = Tk()

#     def __init__(self, blink_image_dir, break_image_dir):
#         self.root.overrideredirect(True)
#         self.root.geometry("100x60+5+5")
#         self.root.lift()
#         self.root.wm_attributes("-topmost", True)

#         self.blink_image = ImageTk.PhotoImage(Image.open(
#             blink_image_dir).resize((100, 60)))
#         self.break_image = ImageTk.PhotoImage(Image.open(
#             break_image_dir).resize((100, 60)))

#         self.image_panel = Label(
#             self.root, highlightthickness=0, borderwidth=0)
#         self.image_panel.grid(sticky="news")

#         # self.root.withdraw()

#     def remind_blink(self):
#         self.remind(self.blink_image)

#     def remind_break(self):
#         self.remind(self.break_image)

#     def remind(self, image):
#         self.set_image(image)
#         self.root.deiconify()
#         self.root.after(5000, lambda: self.root.withdraw())

#     def set_image(self, image):
#         self.image_panel.configure(image=image)
#         self.image_panel.image = image

#     def close(self):
#         self.root.destroy()


# OverlayInstance = Overlay('./assets/images/blink.png',
#                           './assets/images/break.png')


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


# overlay = Overlay()
