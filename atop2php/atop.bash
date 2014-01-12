#!/bin/bash
TXT='/var/www/sochi/atop.txt'
while true; do
        atop | head -30 > $TXT
        echo "<br /> <br />" >> $TXT
        cat /proc/mdstat >> $TXT
        sleep 10
done
