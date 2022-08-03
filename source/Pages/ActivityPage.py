from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from customtkinter import *
from tkinter import *
import numpy as np
from source.Database import database
import matplotlib.pyplot as plt
import matplotlib as mpl
import source.utils.SimpleColor as SimpleColor

def populate_activity_page(frame: CTkFrame):
    
    mpl_color = SimpleColor.text
    mpl.rcParams["text.color"] = mpl_color
    mpl.rcParams["axes.labelcolor"] = mpl_color
    mpl.rcParams["xtick.color"] = mpl_color
    mpl.rcParams["ytick.color"] = mpl_color

    fig = plt.figure(figsize=(6, 9), facecolor=frame["bg"])
    ax1 = fig.add_axes([0.05, 0.95, 0.9, 0.05])
    ax2 = fig.add_axes([0.05, 0.50, 0.9, 0.35])
    ax3 = fig.add_axes([0.05, 0.05, 0.9, 0.35])

    canvas = FigureCanvasTkAgg(fig, master=frame)
    
    def populate_values():
        # ======== Axes 1 ========
        cmap = mpl.cm.cool
        norm = mpl.colors.Normalize(vmin=5, vmax=10)
        cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                        norm=norm,
                                        orientation='horizontal')

        cb1.set_label('Blink Per Minute Frequency')

        # TODO: this.. does nothing? gotta clean em up
        cmap = mpl.colors.ListedColormap(['r', 'g', 'b', 'c'])
        cmap.set_over('0.25')
        cmap.set_under('0.75')

        # ======== Axes 2 ========
        ax2.set_title('Average Blink Per Minute')

        # ======== Axes 3 ========
        ax3.set_title('Latest Session Blink Per Minute')
        
        # Axes 1
        ax1.plot([7]*2, [0,1], 'w')

        # Axes 2
        average = database.get_average(2)
        ax2.bar(average.keys(), average.values())

        # Axes 3
        session_data = database.get_last_session()
        ax3.bar(np.arange(len(session_data)), session_data)

        canvas.draw()

    def on_refresh():
        ax1.clear()
        ax2.clear()
        ax3.clear()
        populate_values()
        pass

    CTkButton(master=frame, text="Refresh", command=on_refresh).pack()
    canvas.get_tk_widget().pack(fill="x", pady=(20,0))

    populate_values()
