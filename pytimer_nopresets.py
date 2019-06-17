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
from tkinter import Tk, PhotoImage

import os
import re
import shlex
import socket
import sys
import time
import tkinter
from tkinter import *
from collections import OrderedDict
from subprocess import PIPE, STDOUT, Popen
from subprocess import call
import tkinter as tk

# Package dependencies:
"""
wmctrl, xdotool, sox and tkinter / tk packages:
Arh based distros: sudo pacman -S tk
Ubuntu:  sudo apt-get install python3-tk
"""

go_on = None    # will be set later

VERSION = '0.1'
MINUTES = 0    # 0 minutes is the default
WINDOW_TITLE = 'pytimer'
DEBUG = True
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
    #return "{:02d}:{:02d}".format(*divmod(sec, 60))
    hours, remainder = divmod(sec, 3600)
    mins, sec = divmod(remainder, 60)
    #if MINUTES > 60:
    return "{:1d}:{:02d}:{:02d}".format(hours, mins, sec)
    #else:
        #return "{:02d}:{:02d}".format(mins, sec)
        #return "{:2d}:{:02d}:{:02d}".format(hours, mins, sec)

def play_sound():
    os.system("play -q -v {vol} {fname} &".format(
        vol=SOUND_VOLUME, fname=SOUND_FILE
    ))


def count_down(event=None):
    global go_on
    go_on = True
    if onset == True: MINUTES = SET
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


def reset(event=None):
    global go_on
    go_on = False
    time_str.set(formatter(MINUTES * 60))
    #clear_vars()
    root.update()
  

def mute(event=None):
    call(["kill", "-9", "play"])

def close(event=None):
    root.destroy()

# SET button code:   
def onset(event=None):
    global SET
    SET = int(entry.get())
    MINUTES = SET
    global onset
    onset = True
    time_str.set(formatter(MINUTES * 60))
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
#root.wm_geometry ("-30-80")
root.wm_geometry ("-2030-0")
root.resizable(width=False, height=False)
#root.geometry('{}x{}'.format(195, 200))

img = PhotoImage(file='/home/swipe/bin/pytimer/pytimer_icon.png')
root.tk.call('wm', 'iconphoto', root._w, img)

mainframe = tk.Frame(root, padx="3",pady="3")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

time_str = tk.StringVar()
# create the time display label, give it a large font
# label auto-adjusts to the font
label_font = ('helvetica', 34)
tk.Label(root, textvariable=time_str, font=label_font, bg='white',
         fg='red', relief='raised', bd=3).grid(padx=5, pady=5)
time_str.set(formatter(MINUTES * 60))
root.update()



# Input box
entry = Entry(root, width=5)
entry.grid(column=0, row=2, pady=5, sticky=(N))
entry.focus()

entry.bind('<Return>', onset)



# create buttons and activates them with enter key
startbtn = tk.Button(root, text='Start', command=count_down)
startbtn.grid(column=0, row=2, sticky=(E))
startbtn.bind('<Return>', count_down)

closebtn = tk.Button(root, text='Close', command=root.destroy)
closebtn.grid(column=0, row=3, sticky=(W))
closebtn.bind('<Return>', close)

resetbtn = tk.Button(root, text='Reset', command=reset)
resetbtn.grid(column=0, row=3, sticky=(N))
resetbtn.bind('<Return>', reset)

mutebtn = tk.Button(root, text='Mute', command=mute)
mutebtn.grid(column=0, row=3, sticky=(E))
mutebtn.bind('<Return>', mute)


setbtn = tk.Button(root, text=' Set ', command=onset)
setbtn.grid(column=0, row=2, sticky=(W))
setbtn.bind('<Return>', onset)



# start the GUI event loop
#root.wm_attributes("-topmost", 1)    # always on top
root.wm_attributes("-topmost", 0)    # never on top
#center(root)
root.mainloop()
