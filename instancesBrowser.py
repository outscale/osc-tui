from osc_sdk_python import Gateway
import curses
import json

gw = Gateway()


def getVms():
    vms = list()
    for vm in gw.ReadVms()["Vms"]:
        tags = vm['Tags']
        print(tags)
       # for t in tags:
        vms.append(tags[0]['Value'])
    return vms


screen = curses.initscr()
curses.cbreak()

screen.border()
num_rows, num_cols = screen.getmaxyx()
curses.noecho()

#screen.addstr(0, 0, "This string gets printed at position (0, 0)")
screen.addstr(num_rows-2, 0, "Press [q] to exit.", curses.A_STANDOUT)
screen.refresh()
my_window = curses.newwin(num_rows - 10, num_cols, 5, 0)
my_window.border()
my_window.addstr(4, 4, "Hello from 4,4")
my_window.refresh()

c = my_window.getch()
while chr(c) != 'q':
    c = my_window.getch()

curses.endwin()
# print(c)
print(getVms())
