from time import time_ns
from source.utils.Config import *
from source.utils.ImageUtils import *
from source.VideoCapture import *
from source.Pages.ActivityPage import ActivityPage
from source.Pages.SettingsPage import populate_settings_page
from source.CustomWidgets import MenuButton, MenuButtonTemplate, NotebookPage
from tkinter.ttk import Notebook, Style
from source.AILogic import AIInstance
from customtkinter import *
from tkinter import *
from PIL import ImageTk, Image


class AppGui:
    # Declare variables & types
    root_tk: CTk
    video_canvas: CTkCanvas
    _height: int
    _width: int
    _menu_font: str = "Helvetica 16 bold"
    _current_page: int
    _page_scroll_handlers: list

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
        self.root_tk.resizable(False, False)
        self.root_tk.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def app_loop(self):
        self.init_videostream()

        next_video_poll = time_ns()

        while True:
            cur_ns = time_ns()
            self.root_tk.update_idletasks()

            if (next_video_poll <= cur_ns):
                # Try to match video FPS
                process_time_start = time_ns()
                self.update_canvas()
                process_time_took = time_ns() - process_time_start
                next_video_poll = min(
                    0, self._video_fps_ns-process_time_took) + time_ns()

            self.root_tk.update()

    def init_window(self, window_title: str):
        self.root_tk.geometry("{0}x{1}".format(self._width, self._height))
        self.root_tk.title(window_title)
        self.root_tk.grid_rowconfigure(1, weight=1)
        self.root_tk.grid_columnconfigure(0, weight=1)

    def init_menu(self):
        self.Menu = CTkFrame(
            master=self.root_tk, width=self._width, height=40, corner_radius=0, fg_color="#212325")
        self.Menu.grid(row=0, column=0, sticky="NEWS", pady=(20, 0))

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

        self.note = Notebook(self.root_tk)
        self.note.grid(column=0, row=1, stick="NEWS", padx=25, pady=(15, 25))

        self.note.bind("<<NotebookTabChanged>>", onTabChange)

        def _on_mousewheel(event):
            if (len(self._page_scroll_handlers) > last_tab):
                self._page_scroll_handlers[last_tab](event)

        # Bind the spinny event
        self.root_tk.bind_all("<MouseWheel>", _on_mousewheel)

    def init_pages(self):

        # initialize each page with scroll
        activity_page, activity_frame, _scroll_handler1 = NotebookPage(
            self.note, self._width, self._height - 105)
        self.note.add(activity_page)

        start_page, start_frame, _scroll_handler2 = NotebookPage(
            self.note, self._width, self._height - 105)
        self.note.add(start_page)

        settings_page, settings_frame, _scroll_handler3 = NotebookPage(
            self.note, self._width, self._height - 105)
        self.note.add(settings_page)

        ActivityPageInstance = ActivityPage(frame=activity_frame)
        ActivityPageInstance.populate_values()
        self.populate_start_page(start_frame)
        populate_settings_page(settings_frame)

        # Hook up the spinny part of your mouse
        self._page_scroll_handlers = [
            _scroll_handler1, _scroll_handler2, _scroll_handler3]

    # ============== START PAGE ==============
    def populate_start_page(self, start_frame):
        # To expand the canvas
        CTkFrame(master=start_frame, width=750, height=0).grid(
            column=0, row=0, columnspan=2)

        # Label for displaying the video stream
        self.video_display = Label(start_frame, justify=CENTER, bg="#2a2d2e")
        self.video_display.grid(row=1, column=0, sticky="ew", columnspan=2)

        # Get all possible video indexes
        video_inputs = VideoCapture.get_cameras()
        video_input_choices = list(
            map(lambda x: "Camera {0}".format(x), video_inputs))

        def combobox_callback(choice):
            camera_choice = video_inputs[video_input_choices.index(choice)]
            self.init_videostream(video_stream=camera_choice)
            print("Changed video input to {0}".format(camera_choice))
            AppConfig.cfg["video"]["camera_index"] = camera_choice
            AppConfig.save_config()

        combobox_var = StringVar(
            value="Camera {0}".format(AppConfig.cfg["video"]["camera_index"]))  # set initial value
        CTkComboBox(start_frame, variable=combobox_var,
                    command=combobox_callback, values=video_input_choices).grid(column=0, row=2, pady=20)

        switch_var = StringVar()

        def toggle_camera():
            if(switch_var.get() == "1"):
                AppConfig.cfg["video"]["show_camera"] = True
            else:
                AppConfig.cfg["video"]["show_camera"] = False
            self.update_canvas()

        CTkSwitch(start_frame, text="Toggle Camera",
                  command=toggle_camera, variable=switch_var).grid(column=1, row=2)

    def init_videostream(self, video_stream=0) -> bool:
        try:
            self.vid = VideoCapture(video_stream)
            self._video_fps_ns = 1000000/self.vid.get_fps()
            return True
        except:
            # Cleanup to prevent some weird errors.
            if hasattr(self, "vid"):
                delattr(self, "vid")
            return False

    def update_canvas(self):
        if AppConfig.cfg["video"]["show_camera"]:
            if hasattr(self, "vid"):
                success, frame = self.vid.get_frame()

                if success:
                    imageResult = AIInstance.process_frame(frame)
                    imageResult = image_resize(
                        imageResult, width=self._width-90)

                    photo = ImageTk.PhotoImage(
                        image=Image.fromarray(imageResult))
                    self.video_display.photo = photo
                    self.video_display.configure(text="", image=photo)
                else:
                    self.video_display.configure(
                        text="Video error. Make sure you have chosen the correct video input.")
            else:
                self.video_display.configure(
                    text="Video error. Make sure you have chosen the correct video input.")

        else:
            blank = Image.new("1", (self._width-40, 520), "white")
            photo = ImageTk.PhotoImage(blank)
            self.video_display.photo = photo
            self.video_display.configure(text="", image=photo)

    def on_window_close(self):
        AIInstance.on_session_finish()

        print("App window closed. Sending exit.")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


AppGuiInstance = AppGui()
