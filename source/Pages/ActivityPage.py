from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)
from customtkinter import *
from tkinter import *
import numpy as np
from source.Database import database
import matplotlib.pyplot as plt
import matplotlib as mpl
from source.utils.Reminder import Reminder
import source.utils.SimpleColor as SimpleColor
from datetime import date, timedelta


class ActivityPage:
    def __init__(self, frame: CTkFrame):
        mpl_color = SimpleColor.text
        mpl.rcParams["text.color"] = mpl_color
        mpl.rcParams["axes.labelcolor"] = mpl_color
        mpl.rcParams["xtick.color"] = mpl_color
        mpl.rcParams["ytick.color"] = mpl_color

        fig = plt.figure(figsize=(6, 9), facecolor=frame["bg"])
        self.ax1 = fig.add_axes([0.05, 0.95, 0.9, 0.05])
        self.ax2 = fig.add_axes([0.05, 0.50, 0.9, 0.35])
        self.ax3 = fig.add_axes([0.05, 0.05, 0.9, 0.35])

        self.canvas = FigureCanvasTkAgg(fig, master=frame)

        self.remark_label = CTkLabel(
            master=frame, text=self.get_remark_message())
        self.remark_label.pack()
        CTkButton(master=frame, text="Refresh", command=self.on_refresh).pack()
        self.canvas.get_tk_widget().pack(fill="x", pady=(20, 0))

        self.populate_values()

    def populate_values(self):
        # ======== Axes 1 ========
        cmap = mpl.cm.cool
        norm = mpl.colors.Normalize(vmin=0, vmax=75)
        cb1 = mpl.colorbar.ColorbarBase(self.ax1, cmap=cmap,
                                        norm=norm,
                                        orientation='horizontal')

        cb1.set_label('Blink Per Minute Frequency')

        # ======== Axes 2 ========
        self.ax2.set_title('Average Blink Per Minute')

        # ======== Axes 3 ========
        self.ax3.set_title('Latest Session Blink Per Minute')

        # Axes 1
        self.ax1.plot([min(75, database.get_session_average())]
                      * 2, [0, 1], 'w')

        # Axes 2
        yesterday_date = (date.today() - timedelta(days=1)).strftime('%d')
        average = database.get_average(
            yesterday_date)
        self.ax2.bar(average.keys(), average.values())

        # Axes 3
        session_data = database.get_last_session()
        self.ax3.bar(np.arange(1, len(session_data)+1), session_data)

        self.canvas.draw()

    def on_refresh(self):
        # TODO: update the color bar

        remark_message = self.get_remark_message()
        self.remark_label.configure(text=remark_message)

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.populate_values()

    def get_remark_message(self):
        # TODO: check if the database is empty or not
        remark = Reminder.get_remarks(database.get_session_average())

        if (remark == 'bad'):
            return 'You have not blinked enough. Please blink more'
        elif (remark == 'ok'):
            return 'You blink enough'
        elif (remark == 'good'):
            return 'You blink more than enough'
        elif (remark == 'great'):
            return 'You blink more than most people'
