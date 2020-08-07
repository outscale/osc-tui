osc-tui:
	python3 -m nuitka osc_tui/main.py -o exe --follow-imports --verbose -o osc-tui
install:
	sudo cp osc-tui /usr/local/bin
uninstall:
	sudo rm /usr/local/bin/osc-tui
