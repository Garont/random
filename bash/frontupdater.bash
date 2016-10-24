#!/bin/bash

#post-recieve hook:
#if repo_path.include? "REPO_NAME.git"
#        system('/home/git/frontupdater/update-front.sh')
#end

HOMEDIR="/home/git/frontupdater"
CMD_LINE="cd /etc/nginx && git reset --hard HEAD && git clean -f -d && git pull && sudo /usr/local/openresty/nginx/sbin/nginx -t && sudo /etc/init.d/openresty reload"
SERVER_LIST=(front1.example.com front2.example.com front3.example.com)
REMOTE_USER="nginxgit"
KEY_FILE="$HOMEDIR/id_rsa"

echo "Got new commit at $(TZ='Europe/Kiev' date +'%Y/%d/%m %H:%M:%S')" >> "$HOMEDIR"/update_front.log
for SERVER in "${SERVER_LIST[@]}" ; do ssh -o StrictHostKeyChecking=no -i "$KEY_FILE" -t -t "$REMOTE_USER"@"$SERVER" "$CMD_LINE" ; done
