if [ "$#" -ne 1 ];then
    echo "Must have only one argument, either --dev or --release."
    exit
fi
EXT=py
cd osc_tui
if [ "$1" == "--dev" ];then
    for i in *; do
        if [ "${i}" != "${i%.${EXT}}" ];then
            sed 's/from osc_tui //g' "$i" > "$i"tmp
            rm "$i"
            mv "$i"tmp "$i"
        fi
    done
elif [ "$1" == "--release" ];then
    for i in *; do
        if [ "${i}" != "${i%.${EXT}}" ];then
            imports=$(grep -v "from" $i | grep import | awk '{print $2}')
            count=0
            for import in $imports
            do
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