#!/bin/bash
while true; do
        atop | head -30 > '/var/www/site/atop.txt'
        sleep 10
done
