osc-tui:
	python3 -m nuitka osc_tui/main.py -o exe --follow-imports --include-package=urllib3 -o osc-tui
install:
	sudo cp osc-tui /usr/local/bin
uninstall:
	sudo rm /usr/local/bin/osc-tui
clean:
	-rm -r main.build osc-tui