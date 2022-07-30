from tkinter import Label
from PIL import Image, ImageTk
import customtkinter
from source.customWidgets import MenuButton, MenuButtonTemplate
from tkinter.ttk import Notebook, Style
import tkinter as tk
from source.AILogic import AIInstance

from source.VideoCapture import *
from time import time_ns
import cv2
import sys


class AppGui:
    # Declare variables & types
    root_tk: customtkinter.CTk
    video_canvas: customtkinter.CTkCanvas
    _height: int
    _width: int
    _menu_font: str = "Helvetica 16 bold"
    _current_page: int

    _menu_bg_color: str
    _active_menu_bg_color: str
    _video_fps_ns: int

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
        #customtkinter.CTkLabel(StartPage, text="start page").grid()
        self.note.add(StartPage)
        # TODO: cleanup
        self.StartPage = StartPage

        # =========== Settings Page ===========

        SettingsPage = customtkinter.CTkFrame(master=self.note,
                                              width=200,
                                              height=200,
                                              corner_radius=10)
        self.note.add(SettingsPage)

        # Create a canvas that can fit the above video source size
        #self.scrollbar = customtkinter.CTkScrollbar()
        # self.video_canvas = customtkinter.CTkCanvas(
        #    StartPage, width=640, height=480)
        #self.video_canvas.grid(column=0, row=0, sticky="news")

        # naming is hard, kill me now
        self.video_display = tk.Label(
            self.StartPage)
        self.video_display.grid()

        # self.scrollbar = customtkinter.CTkScrollbar(
        #     StartPage, command=self.video_canvas.yview)
        # self.scrollbar.grid(row=0, column=1, sticky="ns")

        # self.video_canvas.configure(yscrollcommand=self.scrollbar.set)

    def app_loop(self):
        self.init_videostream()

        next_video_poll = time_ns()

        while True:
            self.root_tk.update_idletasks()
            if (next_video_poll <= time_ns()):
                # Try to match video FPS
                process_time_start = time_ns()
                self.update_canvas()
                process_time_took = time_ns() - process_time_start
                print("Took {0} ns".format(process_time_took))
                next_video_poll = min(
                    0, self._video_fps_ns-process_time_took) + time_ns()
            self.root_tk.update()

    def init_videostream(self, video_stream=1):
        self.vid = VideoCapture(video_stream)
        self._video_fps_ns = 1000000/self.vid.get_fps()

    def update_canvas(self):
        success, frame = self.vid.get_frame()

        if success:
            imageResult = AIInstance.process_frame(frame)
            photo = ImageTk.PhotoImage(image=Image.fromarray(imageResult))
            self.video_display.photo = photo
            self.video_display.configure(image=photo)
            #self.video_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.root_tk.after(1, self.update_canvas)
