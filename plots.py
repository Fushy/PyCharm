import sys
import threading

import keyboard
import matplotlib
import matplotlib.dates
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

from Times import elapsed_seconds, now

colors = {"blue": 'b', "green": 'g', "red": 'r', "cyan": 'c', "magenta": 'm', "yellow": 'y', "black": 'k', "white": 'w'}
colors_order = "bk"

class CursorPlt(object):
    def __init__(self, ax):
        self.ax = ax
        self.lx = ax.axhline(color='k')  # the horiz line
        self.ly = ax.axvline(color='k')  # the vert line

        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)

    def on_mouse_move(self, event):
        if not event.inaxes:
            return

        xx, yy = event.xdata, event.ydata
        # update the line positions
        self.lx.set_ydata(yy)
        # self.ly.set_xdata(xx)

        # self.txt.set_text('x=%1.2f, y=%1.2f' % (xx, yy))
        self.txt.set_text('y=%1.2f' % (yy,))
        plt.draw()


def exit_event(event):
    if event.button == 3:
        print(event)
        plt.close('all')
        sys.exit()


def wait_key_press(i):
    while not keyboard.is_pressed("right") and not keyboard.is_pressed("left"):
        plt.pause(.005)
    start = now()
    if keyboard.is_pressed("right"):
        while keyboard.is_pressed("right"):
            plt.pause(.005)
            if elapsed_seconds(start) >= 0.5:
                break
        i += 1
    if keyboard.is_pressed("left"):
        while keyboard.is_pressed("left"):
            plt.pause(.005)
            if elapsed_seconds(start) >= 0.5:
                break
        i -= 1
    is_looping = elapsed_seconds(start) >= 0.5
    return i, is_looping


def init_gui(plt, axis_color, fig=None, fullscreen=True, title="", date_format=None, qt=True, n_subplots=1) -> plt:
    curve_color = "#0F1623"
    # plt.figure(facecolor="black")
    plt.rcParams['figure.figsize'] = (16, 8)
    plt.rcParams["keymap.zoom"].append("a")
    plt.rcParams["keymap.back"].append("²")
    if "left" in plt.rcParams["keymap.back"]:
        plt.rcParams["keymap.back"].remove("left")
        plt.rcParams["keymap.forward"].remove("right")
    plt.rcParams["text.color"] = "white"
    plt.rcParams['axes.facecolor'] = curve_color
    plt.rcParams['axes.titley'] = 1.0
    plt.rcParams['axes.titlepad'] = -85

    # # matplotlib.use("module://backend_interagg")
    if qt and threading.current_thread() == threading.main_thread():
        # print(matplotlib.get_backend())
        matplotlib.use("Qt5agg")

    fig, axs = plt.subplots(n_subplots)
    if n_subplots == 1:
        axs = [axs]
    # ax = plt.gca()
    for i in range(len(fig.axes)):
        ax = axs[i]
        # plt.tight_layout(pad=3, w_pad=0, h_pad=0)
        ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
        ax.spines['bottom'].set_color(axis_color)
        ax.spines['top'].set_color(axis_color)
        ax.spines['right'].set_color(axis_color)
        ax.spines['left'].set_color(axis_color)
        ax.tick_params(axis='x', colors=axis_color)
        ax.tick_params(axis='y', colors=axis_color)
        if date_format is not None:
            if date_format == "":
                date_format = '%Y-%m-%d %Hh%mm'
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(date_format))
        # plt.setp(ax.get_xticklabels(), rotation=-20, fontsize=10)
        # ax.set_xticks(np.arange(0, 100, 10))
        plt.connect('motion_notify_event', Cursor(ax, color="black", linewidth=0.5))

    if fig is None:
        fig: plt.figure = plt.figure()
    if fullscreen:
        fig.canvas.manager.full_screen_toggle()
    fig.patch.set_facecolor(curve_color)
    fig.canvas.mpl_connect('button_press_event', exit_event)
    # plotting(axis_color, plt, x, y)

    # plt.xticks(range(100))
    # plt.setp(ax.get_xticklabels(), rotation=-20, fontsize=1)
    fig.suptitle(title)
    # fig.tight_layout()
    return plt, axs, fig
