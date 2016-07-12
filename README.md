Count down seconds from a given minute value
using the Tkinter GUI toolkit that comes with Python.

Basic Tk version by vegaseat:
https://www.daniweb.com/programming/software-development/threads/464062/countdown-clock-with-python

Script based on Pomodoro-Timer:
Laszlo Szathmary, alias Jabba Laci https://github.com/jabbalaci/Pomodoro-Timer

Modified by: Swipe650 https://github.com/Swipe650

Screenshot
---------

![pytimer](screenshot.png)

Usage
-----

Create an application launcher and execute ./launcher.sh for countdown timer with basic presets

For a custom timer execute $ ./pytimer.py X' or $ './launcher.sh X' (where X = number of minutes)

Dependencies
------------

Install the following packages with your package manager:
* wmctrl
* xdotool
* sox

The GUI is based on Tkinter. For Python 3 I had to install it too


TODO: add an input box for time required and a button to increment time remianing by 1 mintue 
