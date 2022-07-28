from tkinter import Label
import customtkinter
from source.customWidgets import MenuButton, MenuButtonTemplate
from tkinter.ttk import Notebook, Style


class AppGui:
    # Declare variables & types
    root_tk: customtkinter.CTk
    _height: int
    _width: int
    _menu_font: str = "Helvetica 16 bold"
    _current_page: int

    _menu_bg_color: str
    _active_menu_bg_color: str

    # Main Window Setup
    def __init__(self, width=800, height=500):
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")
        self.root_tk = customtkinter.CTk()
        self._width = width
        self._height = height

    def init_window(self, window_title: str):
        self.root_tk.geometry("{0}x{1}".format(self._width, self._height))
        self.root_tk.title(window_title)
        self.root_tk.grid_rowconfigure(1, weight=1)
        self.root_tk.grid_columnconfigure(0, weight=1)

    def init_menu(self):
        self.Menu = customtkinter.CTkFrame(
            master=self.root_tk, width=self._width, height=75, corner_radius=0, fg_color="#212325")
        self.Menu.grid(row=0, column=0, sticky="NEWS")

        self.Menu.grid_columnconfigure(0, weight=1)
        self.Menu.grid_columnconfigure(1, weight=1)
        self.Menu.grid_columnconfigure(2, weight=1)

        menu_btn = MenuButtonTemplate(self.Menu, self._menu_font)

        self.ActivityButton = menu_btn("Activity", lambda: self.note.select(0), selected=True)
        self.StartButton = menu_btn("Start", lambda: self.note.select(1))
        self.SettingsButton = menu_btn("Settings", lambda: self.note.select(2))

        # TODO: Cleanup this UI thinggy.
        button_maps: list[Label] = [self.ActivityButton, self.StartButton, self.SettingsButton]
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

        # =========== Activity Page ===========
        ActivityPage = customtkinter.CTkFrame(master=self.note,
                                              width=200,
                                              height=200,
                                              corner_radius=10)
        customtkinter.CTkLabel(ActivityPage, text="activity page").grid()
        self.note.add(ActivityPage)

        # =========== Start Page ===========

        StartPage = customtkinter.CTkFrame(master=self.note,
                                           width=200,
                                           height=200,
                                           corner_radius=10)
        customtkinter.CTkLabel(StartPage, text="start page").grid()
        self.note.add(StartPage)

        # =========== Settings Page ===========

        SettingsPage = customtkinter.CTkFrame(master=self.note,
                                              width=200,
                                              height=200,
                                              corner_radius=10)
        self.note.add(SettingsPage)

        # Create a canvas that can fit the above video source size
        self.scrollbar = customtkinter.CTkScrollbar()
        self.canvas = customtkinter.CTkCanvas(
            StartPage, width=640, height=480)
        self.canvas.grid(column=0, row=0, sticky="news")

        self.scrollbar = customtkinter.CTkScrollbar(
            StartPage, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
