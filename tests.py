from osc_sdk_python import Gateway
import curses
import json
from ocnWindow import OcnWindow

screen = curses.initscr()
curses.cbreak()
curses.curs_set(0)

screen.border()
num_rows, num_cols = screen.getmaxyx()
curses.noecho()

#screen.addstr(0, 0, "This string gets printed at position (0, 0)")
o = OcnWindow(num_cols, num_rows - 10, 0, 5, "1245", True)
OcnWindow(num_cols, 5, 0, 0, "1245", True)

c = o.getch()
while chr(c) != 'q':
    c = o.getch()
#screen.refresh()


curses.endwin()
#print(c)
