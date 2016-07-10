#!/usr/bin/env python3
# encoding: utf-8

"""
Count down seconds from a given minute value
using the Tkinter GUI toolkit that comes with Python.

Basic Tk version by vegaseat (I extended this):
https://www.daniweb.com/programming/software-development/threads/464062/countdown-clock-with-python
Laszlo Szathmary, alias Jabba Laci https://github.com/jabbalaci/Pomodoro-Timer

Modified by: Swipe650 https://github.com/Swipe650
"""

import os
import re
import shlex
import socket
import sys
import time
from collections import OrderedDict
from subprocess import PIPE, STDOUT, Popen

# Manjaro: sudo pacman -S tk
# Ubuntu:  sudo apt-get install python3-tk
import tkinter as tk

go_on = None    # will be set later

VERSION = '0.1'
MINUTES = 10    # 25 minutes is the default
WINDOW_TITLE = 'pytimer'
DEBUG = False
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = '{d}/timer_done.wav'.format(d=PROJECT_DIR)
SOUND_VOLUME = '0.75'

hostname = socket.gethostname()
if hostname == 'laptop':
    SOUND_VOLUME = 0.75

required_commands = [
    '/usr/bin/wmctrl',      # in package wmctrl
    '/usr/bin/xdotool',     # in package xdotool
    '/usr/bin/play',        # in package sox
]


def check_required_commands():
    """
    Verify if the external binaries are available.
    """
    for cmd in required_commands:
        if not os.path.isfile(cmd):
            print("Error: the command '{0}' is not available! Abort.".format(cmd))
            sys.exit(1)

check_required_commands()


###################################
## window and process management ##
###################################

def get_simple_cmd_output(cmd, stderr=STDOUT):
    """
    Execute a simple external command and get its output.

    The command contains no pipes. Error messages are
    redirected to the standard output by default.
    """
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0].decode("utf8")


def get_wmctrl_output():
    """
    Parses the output of wmctrl and returns a list of ordered dicts.
    """
    cmd = "wmctrl -lGpx"
    lines = [line for line in get_simple_cmd_output(cmd)
             .encode('ascii', 'ignore')
             .decode('ascii').split("\n") if line]

    res = []
    for line in lines:
        pieces = line.split()
        d = OrderedDict()
        d['wid'] = pieces[0]
        d['desktop'] = int(pieces[1])
        d['pid'] = int(pieces[2])
        d['geometry'] = [int(x) for x in pieces[3:7]]
        d['window_class'] = pieces[7]
        d['client_machine_name'] = pieces[8]
        d['window_title'] = ' '.join(pieces[9:])
        res.append(d)
    #
    return res


def get_wid_by_title(title_regexp):
    """
    Having the window title (as a regexp), return its wid.

    If not found, return None.
    """
    for d in get_wmctrl_output():
        m = re.search(title_regexp, d['window_title'])
        if m:
            return d['wid']
    #
    return None


def activate_window_by_id(wid):
    """
    Put the focus on and activate the the window with the given ID.
    """
    os.system('xdotool windowactivate {wid}'.format(wid=wid))


def switch_to_window(title_regexp):
    """
    Put the focus on the window with the specified title.
    """
    wid = get_wid_by_title(title_regexp)
    if wid:
        if DEBUG:
            print('# window id:', wid)
        wid = int(wid, 16)
        if DEBUG:
            print('# switching to the other window')
        activate_window_by_id(wid)
    else:
        if DEBUG:
            print('# not found')


#########
## GUI ##
#########

def formatter(sec):
    # format as 2 digit integers, fills with zero to the left
    # divmod() gives minutes, seconds
    return "{:02d}:{:02d}".format(*divmod(sec, 60))


def play_sound():
    os.system("play -q -v {vol} {fname} &".format(
        vol=SOUND_VOLUME, fname=SOUND_FILE
    ))


def count_down():
    global go_on
    go_on = True
    for t in range(MINUTES * 60 - 1, -1, -1):
        if t == 0:
            play_sound()
            switch_to_window(WINDOW_TITLE)
        time_str.set(formatter(t))
        root.update()
        # delay one second
        for _ in range(2):
            time.sleep(0.5)    # if minimized then maximized,
            root.update()      # it's more responsive this way
        if not go_on:
            return
    reset()


def reset():
    global go_on
    go_on = False
    time_str.set(formatter(MINUTES * 60))
    root.update()
    
def five():
    global go_on
    go_on = False
    time_str.set(formatter(5 * 60))
    root.update()

def ten():
    global go_on
    go_on = False
    time_str.set(formatter(10 * 60))
    root.update()
    
def fifteen():
    global go_on
    go_on = False
    time_str.set(formatter(15 * 60))
    root.update()

def twenty():
    global go_on
    go_on = False
    time_str.set(formatter(20 * 60))
    root.update()
    
def twentyfive():
    global go_on
    go_on = False
    time_str.set(formatter(25 * 60))
    root.update()   

def thirty():
    global go_on
    go_on = False
    time_str.set(formatter(30 * 60))
    root.update()

def seven():
    global go_on
    go_on = False
    time_str.set(formatter(7 * 60))
    root.update()

def twentytwo():
    global go_on
    go_on = False
    time_str.set(formatter(22 * 60))
    root.update()


def center(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center

    from http://stackoverflow.com/a/10018670/232485
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


def print_usage():
    print("""
Swipe650's Pytimer v{ver}

Usage: {fname} [parameter]

Parameters:
-h, --help        this help
-play             play the sound and quit (for testing the volume)
<minutes>         If not specified, then the default value is 10.
""".strip().format(ver=VERSION, fname=sys.argv[0]))

if len(sys.argv) > 1:
    param = sys.argv[1]
    if param in ['-h', '--help']:
        print_usage()
        sys.exit(0)
    elif param == '-play':
        # for testing the volume
        play_sound()
        sys.exit(0)
    elif re.search(r'\d+', param):
        try:
            MINUTES = int(param)
        except ValueError:
            print("Error: unknown option.")
            sys.exit(1)
    else:
        print("Error: unknown option.")
        sys.exit(1)


root = tk.Tk()
root.wm_title(WINDOW_TITLE)
root.wm_geometry ("-100-100")
root.resizable(width=False, height=False)
root.geometry('{}x{}'.format(190, 230))

time_str = tk.StringVar()
# create the time display label, give it a large font
# label auto-adjusts to the font
label_font = ('helvetica', 40)
tk.Label(root, textvariable=time_str, font=label_font, bg='white',
         fg='red', relief='raised', bd=3).pack(fill='x', padx=5, pady=5)
time_str.set(formatter(MINUTES * 60))
root.update()
# create buttons
# pack() positions the buttons below the label
#tk.Button(root, text='Start', command=count_down).pack(side="left")
tk.Button(root, text='Start', command=count_down).place(relx=.15, rely=.45, anchor="c")
#(relheight=.25, relwidth=.35)
#tk.Button(root, text='Close', command=root.destroy).pack(side='bottom')
tk.Button(root, text='Close', command=root.destroy).place(relx=.15, rely=.90, anchor="c")
#tk.Button(root, text='Reset', command=reset).pack(side="left")
tk.Button(root, text='5min ', command=five).place(relx=.50, rely=.45, anchor="c")
tk.Button(root, text='10min', command=ten).place(relx=.80, rely=.45, anchor="c")
tk.Button(root, text='15min', command=fifteen).place(relx=.50, rely=.60, anchor="c")
tk.Button(root, text='20min', command=twenty).place(relx=.80, rely=.60, anchor="c")
tk.Button(root, text='25min', command=twentyfive).place(relx=.50, rely=.75, anchor="c")
tk.Button(root, text='30min', command=thirty).place(relx=.80, rely=.75, anchor="c")
tk.Button(root, text='22min', command=twentytwo).place(relx=.50, rely=.90, anchor="c")
tk.Button(root, text='7min ', command=seven).place(relx=.80, rely=.90, anchor="c")

# start the GUI event loop
#root.wm_attributes("-topmost", 1)    # always on top
root.wm_attributes("-topmost", 0)    # always on top
#center(root)
root.mainloop()
