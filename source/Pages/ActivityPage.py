from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from customtkinter import *
from tkinter import *
import numpy as np
from source.Database import database
import matplotlib.pyplot as plt
import matplotlib as mpl


def populate_activity_page(frame):
    CTkFrame(master=frame, width=750, height=0).pack()

    fig = plt.figure(figsize=(6, 10))
    ax1 = fig.add_axes([0.05, 0.90, 0.9, 0.05])
    ax2 = fig.add_axes([0.05, 0.55, 0.9, 0.25])
    ax3 = fig.add_axes([0.05, 0.20, 0.9, 0.25])

    # ======== Axes 1 ========
    cmap = mpl.cm.cool
    norm = mpl.colors.Normalize(vmin=5, vmax=10)
    cb1 = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax1,
                       norm=norm,
                       orientation='horizontal')

    cb1.ax.plot([7]*2, [0, 1], "w")  # TODO: put in proper values
    cb1.ax.set_title('Remarks')
    cb1.set_label('Blink Per Minute Frequency')

    cmap = mpl.colors.ListedColormap(['r', 'g', 'b', 'c'])
    cmap.set_over('0.25')
    cmap.set_under('0.75')

    # ======== Axes 2 ========
    average = database.get_average(2)  # TODO: get date of day before
    ax2.bar(average.keys(), average.values())
    ax2.set_title('Average Blink Per Minute')

    # ======== Axes 3 ========

    session_data = database.get_last_session()
    ax3.plot(np.arange(len(session_data)), session_data, marker="o")
    ax3.set_title('Latest Session Blink Per Minute')

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

    def on_refresh():
        # canvas.draw()
        pass

    CTkButton(master=frame, text="Refresh", command=on_refresh).pack()
