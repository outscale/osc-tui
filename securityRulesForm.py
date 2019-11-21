import curses

import npyscreen

import securityRulesGrid
import securityRulesInspector


class SecurityRulesForm(npyscreen. FormBaseNew):
    def __init__(self, *args, **keywords):
        super().__init__(*args, **keywords)

    def create(self):
        y, _ = self.useable_space()
        self.draw_line_at = int(y-9)
        a = None

        def on_selection(line):
            a.set_value(line)
        securityRulesGrid.add_security_rules_grid(self, on_selection)
        a = securityRulesInspector.add_security_rules_inspector(self)

    def draw_form(self,):
        _, MAXX = self.curses_pad.getmaxyx()
        super(SecurityRulesForm, self).draw_form()
        self.curses_pad.hline(self.draw_line_at, 1, curses.ACS_HLINE, MAXX-2)
