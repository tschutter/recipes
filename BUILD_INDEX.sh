#!/bin/sh
#
# Create index.html
#

echo "<!doctype html public "-//W3C//DTD HTML 3.2 Final//EN">" > index.html
echo "<html>" >> index.html
echo "<head>" >> index.html
echo "<title>recipes</title>" >> index.html
echo "</head>" >> index.html
echo "<h1 align=\"center\">recipes</h1>" >> index.html
echo "<ul>" >> index.html

for FILE in `ls *.txt`; do
    if [ "${FILE}" = "TEMPLATE.txt" ]; then continue; fi
    TITLE=`head -n 1 $FILE`
    echo "  <li><a href=\"${FILE}\">${TITLE}</a></li>" >> index.html
done

echo "</ul>" >> index.html
echo "</body>" >> index.html
echo "</html>" >> index.html
