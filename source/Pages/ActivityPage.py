import time
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
from scipy.interpolate import make_interp_spline


class ActivityPage:
    def __init__(self, frame: CTkFrame):
        mpl_color = SimpleColor.text
        mpl.rcParams["text.color"] = mpl_color
        mpl.rcParams["axes.labelcolor"] = mpl_color
        mpl.rcParams["xtick.color"] = mpl_color
        mpl.rcParams["ytick.color"] = mpl_color

        fig = plt.figure(figsize=(6, 9), facecolor=frame["bg"])
        self.ax1 = fig.add_axes([0.05, 0.95, 0.9, 0.05])
        self.ax2 = fig.add_axes([0.10, 0.50, 0.8, 0.35])
        self.ax3 = fig.add_axes([0.10, 0.05, 0.8, 0.35])

        bg_color = SimpleColor.window_bg
        self.ax1.set_facecolor(bg_color)
        self.ax2.set_facecolor(bg_color)
        self.ax3.set_facecolor(bg_color)

        self.canvas = FigureCanvasTkAgg(fig, master=frame)

        self.remark_label = CTkLabel(
            master=frame, text=self.get_remark_message())
        self.remark_label.pack()
        CTkButton(master=frame, text="Refresh", command=self.on_refresh).pack()

        # customtkinter's scaling tracker wth
        self.canvas.get_tk_widget().pack(fill="x", pady=(
            20, (ScalingTracker.get_widget_scaling(self.canvas.get_tk_widget())-1)*1000))

    def populate_values(self):
        # ======== Axes 1 ========
        session_average = database.get_session_average()
        cmap = mpl.cm.cool
        norm = mpl.colors.Normalize(vmin=0, vmax=75)
        cb1 = mpl.colorbar.ColorbarBase(self.ax1, cmap=cmap,
                                        norm=norm,
                                        orientation='horizontal')
        if (session_average):
            self.ax1.plot(
                [min(75, database.get_session_average())]*2, [0, 1], 'w', linewidth=3)
        cb1.set_label('Last Session\'s blink average')

        # ======== Axes 2 ========
        yesterday_date = (date.today() - timedelta(days=1)).strftime('%d')
        year = time.strftime('%Y', time.localtime())
        month = time.strftime('%m', time.localtime())
        average = database.get_average(year, month, yesterday_date)
        self.ax2.bar(average.keys(), average.values())
        self.ax2.set_title('Average Blink Per Minute Past 24 hours')
        self.ax2.set_xticks(np.arange(1, 25, 1.0))
        self.ax2.set_xlabel('Hours')
        self.ax2.set_ylabel('Average Blinks Per Hour')

        # ======== Axes 3 ========
        session_data = database.get_last_session()

        if (session_data):
            x3 = np.arange(1, len(session_data)+1)
            y3 = session_data

            color = next(self.ax3._get_lines.prop_cycler)['color']

            if (len(session_data) > 3):  # TODO: for debugging purposes only
                spline = make_interp_spline(x3, y3)
                x3hat = np.linspace(x3.min(), x3.max(), 500)
                y3hat = spline(x3hat)
                self.ax3.plot(x3hat, y3hat, color=color)
                self.ax3.fill_between(
                    x=x3hat, y1=y3hat, color=color, alpha=0.2)

            self.ax3.plot(x3, y3, "o", color=color)

            self.ax3.set_title('Latest Session Blink Per Minute')
            self.ax3.set_xlabel('Minutes')
            self.ax3.set_ylabel('Blink Count')

        self.canvas.draw()

    def on_refresh(self):
        remark_message = self.get_remark_message()
        self.remark_label.configure(text=remark_message)

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.populate_values()

    def get_remark_message(self):
        session_average = database.get_session_average()
        if (not session_average):
            return 'Please record a session to see the average blinks per minute on the last session'

        remark = Reminder.get_remarks(session_average)

        if (remark == 'bad'):
            return 'You have not blinked enough. Please blink more'
        elif (remark == 'ok'):
            return 'You blink enough'
        elif (remark == 'good'):
            return 'You blink more than enough'
        elif (remark == 'great'):
            return 'You blink more than most people'
