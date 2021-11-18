all: npyscreen/README.md osc-tui

npyscreen/README.md:
	git submodule update --init

appimage-bld/create.sh:
	git submodule update --init

osc-tui-x86_64.AppImage: appimage-bld/osc-tui-x86_64.AppImage
	cp appimage-bld/osc-tui-x86_64.AppImage osc-tui-x86_64.AppImage

appimage-bld/osc-tui-x86_64.AppImage: appimage-bld/create.sh
	cd appimage-bld/ && ./create.sh --wget-appimagetool --source-path=../ 

osc-tui: npyscreen/README.md
	python3 -m nuitka osc_tui/main.py -o exe --follow-imports --include-package=urllib3 -o osc-tui
install:
	cp osc-tui /usr/local/bin
uninstall:
	rm /usr/local/bin/osc-tui
clean:
	rm -rvf main.build osc-tui

.PHONY: clean install uninstall
