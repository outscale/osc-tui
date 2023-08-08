appimage-bld/create.sh:
	git submodule update --init

osc-tui-x86_64.AppImage: appimage-bld/osc-tui-x86_64.AppImage
	cp appimage-bld/osc-tui-x86_64.AppImage osc-tui-x86_64.AppImage

appimage-bld/osc-tui-x86_64.AppImage: appimage-bld/create.sh
	cd appimage-bld/ && ./create.sh --wget-appimagetool --source-path=../ --py3_ver=3.11

.PHONY:
