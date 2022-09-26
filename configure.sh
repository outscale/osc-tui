#!/bin/bash

if [ "$#" -ne 1 ];then
    echo "Must have only one argument, either --dev or --release."
    exit
fi
EXT=py
cd osc_tui
if [ "$1" == "--dev" ];then
# All imports of files from the projects have to be direct.
# no more "from osc_tui import ...".
    for i in *; do
        if [ "${i}" != "${i%.${EXT}}" ];then
            # Replace all "from osc_tui " by "".
            # Write to a tmp file.
            sed 's/from osc_tui //g' "$i" > "$i"tmp
            # Remove the old file.
            rm "$i"
            # Move the tmp file instead.
            mv "$i"tmp "$i"
        fi
    done
elif [ "$1" == "--release" ];then
# All imports have to come from osc_tui.
# So we add "from osc_tui before all imports from the projects."
    for i in *; do
        if [ "${i}" != "${i%.${EXT}}" ];then
            # Get a list of all directs imports. Not beginning by "from".
            imports=$(grep -v "from" $i | grep import | awk '{print $2}')
            count=0
            for import in $imports
            do
            # For each import, if it is an osc_tui's python file,
            # we do the replacement job.
            if test -f "$import".py; then
                sed "s/^import "$import"$/from osc_tui import "$import"/g" "$i" > "$i"tmp
                rm "$i"
                mv "$i"tmp "$i"
            fi
            done

        fi
    done
else
    echo "Must have only one argument, either --dev or --release."
    exit
fi
