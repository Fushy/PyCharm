import sys
import threading

import matplotlib
import matplotlib.dates
import matplotlib.pyplot as plt
from matplotlib import pyplot


class CursorPlt(object):
    """ ? """
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


def init_gui(plt, axis_color, fig=None, fullscreen=True, title="", date_format=None) -> plt:
    curve_color = "#0F1623"
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
    if threading.current_thread() == threading.main_thread():
        # print(matplotlib.get_backend())
        matplotlib.use("Qt5agg")
    # matplotlib.use("module://backend_interagg")
    if fig is None:
        fig: plt.figure = plt.figure()
        if fullscreen:
            fig.canvas.manager.full_screen_toggle()
    fig.patch.set_facecolor(curve_color)
    fig.canvas.mpl_connect('button_press_event', exit_event)
    # plotting(axis_color, plt, x, y)
    ax = plt.gca()
    plt.tight_layout(pad=3, w_pad=0, h_pad=0)
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
    plt.setp(ax.get_xticklabels(), rotation=-20)
    fig.suptitle(title)
    fig.tight_layout()
    return plt, ax, fig
