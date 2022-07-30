from source.customWidgets import MenuButton, MenuButtonTemplate, NotebookPage
from tkinter.ttk import Notebook, Style
from source.AILogic import AIInstance
from customtkinter import *
from tkinter import *
from PIL import ImageTk
import PIL

from source.VideoCapture import *


class AppGui:
    # Declare variables & types
    root_tk: CTk
    video_canvas: CTkCanvas
    _height: int
    _width: int
    _menu_font: str = "Helvetica 16 bold"
    _current_page: int

    _menu_bg_color: str
    _active_menu_bg_color: str
    _video_fps_ns: int

    # Main Window Setup
    def __init__(self, width=800, height=500):
        set_appearance_mode("System")
        set_default_color_theme("blue")
        self.root_tk = CTk()
        self._width = width
        self._height = height

    def init_window(self, window_title: str):
        self.root_tk.geometry("{0}x{1}".format(self._width, self._height))
        self.root_tk.title(window_title)
        self.root_tk.grid_rowconfigure(1, weight=1)
        self.root_tk.grid_columnconfigure(0, weight=1)

    def init_menu(self):
        self.Menu = CTkFrame(
            master=self.root_tk, width=self._width, height=75, corner_radius=0, fg_color="#212325")
        self.Menu.grid(row=0, column=0, sticky="NEWS")

        self.Menu.grid_columnconfigure(0, weight=1)
        self.Menu.grid_columnconfigure(1, weight=1)
        self.Menu.grid_columnconfigure(2, weight=1)

        menu_btn = MenuButtonTemplate(self.Menu, self._menu_font)

        self.ActivityButton = menu_btn(
            "Activity", lambda: self.note.select(0), selected=True)
        self.StartButton = menu_btn("Start", lambda: self.note.select(1))
        self.SettingsButton = menu_btn("Settings", lambda: self.note.select(2))

        # TODO: Cleanup this UI thinggy.
        button_maps: list[Label] = [self.ActivityButton,
                                    self.StartButton, self.SettingsButton]
        for i in range(len(button_maps)):
            button_maps[i].grid(column=i, row=0)
        last_tab: int = 0

        def onTabChange(e):
            nonlocal last_tab
            tab_id = e.widget.index(e.widget.select())
            button_maps[tab_id].event_generate("<<MenuSelect>>")
            button_maps[last_tab].event_generate("<<MenuDeSelect>>")
            last_tab = tab_id

        noteStyle = Style()
        noteStyle.theme_use("default")
        noteStyle.layout("TNotebook.Tab", [])
        noteStyle.configure("TNotebook", background="#212325", borderwidth=0)
        noteStyle.configure(
            "TNotebook.Tab", background="#212325", borderwidth=0)
        noteStyle.map("TNotebook", background=[("selected", "#212325")])

        self.note = Notebook(self.root_tk, padding=25)
        self.note.grid(column=0, row=1, stick="NEWS")

        self.note.bind("<<NotebookTabChanged>>", onTabChange)

    def init_pages(self):

        # initialize each page with scroll
        activity_page, activity_frame = NotebookPage(
            self.note, self._width, self._height - 105)
        self.note.add(activity_page)

        start_page, start_frame = NotebookPage(
            self.note, self._width, self._height - 105)
        self.note.add(start_page)

        settings_page, settings_frame = NotebookPage(
            self.note, self._width, self._height - 105)
        self.note.add(settings_page)

        # Fill in activity page with buttons
        for thing in range(20):
            Button(activity_frame, text=f'Button {thing} Yo!').grid(
                row=thing, column=0, pady=10, padx=10)

        # Label for displaying the video stream
        self.video_display = Label(
            start_frame)
        self.video_display.grid()

    def init_videostream(self, video_stream=1):
        self.vid = VideoCapture(video_stream)
        self._video_fps_ns = 1000000/self.vid.get_fps()

    def update_canvas(self):
        success, frame = self.vid.get_frame()

        if success:
            imageResult = AIInstance.process_frame(frame)
            # TODO: Fix the image PIL thing lmao. It's so messy
            photo = ImageTk.PhotoImage(image=PIL.Image.fromarray(imageResult))
            self.video_display.photo = photo
            self.video_display.configure(image=photo)
        self.root_tk.after(1, self.update_canvas)
