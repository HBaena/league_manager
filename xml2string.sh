#! /bin/bash/

files=$(ls *.glade)

for file in $files; do
    echo $file' = """'
    string=$(cat $file)
    echo $string
    echo '"""'
    echo
done