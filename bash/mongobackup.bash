#!/bin/bash

NODES_ARRAY=(somenode{1..4}.example.com)
BACKUP_DIR="/backup/mongo"
LOGS_DIR="/var/log/backup"
MONGODB_PORT="27017"
CONFIG_PORT="37019"
BACKUP_DBS_LIST=(db1 db2 config)
EMAILS="rashkur@gmail.com, someotherguy@example.com"
BACKUP_STORE_DAYS=30

STATE="Ok"
function Maaam {
     echo $1 | mail -s "Backup Fuckup" $EMAILS
}

function CheckState {
    if [ "$STATE" != "Ok" ]
        then
        Maaam "$STATE"
    fi
}



#fix for ipv6 mongodump
c=0
for i in "${NODES_ARRAY[@]}" ; do
         NODES_ARRAY["$c"]="[$(dig AAAA $i +short)]"
         c=$((c+1))
done

CONFIG_BACKUP_NODE="${NODES_ARRAY[0]}"


#at first we goiing trought all mongos and collection temptables, which shouldn't be backed up
unset TMP_COLL_ARR
declare -a TMP_COLL_ALL
for node in "${NODES_ARRAY[@]}"
        do
        result=$(LC_ALL=C mongo --ipv6 "$node":"$MONGODB_PORT"/clickky --quiet --eval 'db.isMaster().ismaster')
        if [[ "$result" = "true" ]]
        then
            c=0
            for table in $(LC_ALL=C mongo --ipv6 "$node":"$MONGODB_PORT"/clickky --quiet --eval 'db.getCollectionNames()' | tr "," "\n" | grep 'tmp\..*') ; do
                TMP_COLL_ARR["$c"]=" --excludeCollection $table "
                c=$((c+1))
            done
        fi
done

#Backing up mogdo, excluding tmp tables
for node in ${NODES_ARRAY[@]}
        do
        result="$(LC_ALL=C mongo --ipv6 "$node":"$MONGODB_PORT"/clickky --quiet --eval 'db.isMaster().ismaster')"
        if [[ "$result" = "false" ]]
        then
             LOGPATH="$LOGS_DIR/$node".$(date +'%Y-%m-%d').log
             echo -ne "$node not master. Starting backup procedure \r\n"
             mongodump -h "$node":"$MONGODB_PORT" --db clickky --out "$BACKUP_DIR" ${TMP_COLL_ARR[@]} &> "$LOGPATH" 2>&1
             #| while read output ; do echo -ne "$output \r" ; sleep 1 ; done
             tail -1 "$LOGPATH" | grep 'done dumping' &> /dev/null && STATE="Ok"|| STATE="Backup from $node Broken"
        fi
done

CheckState

STATE="Ok"
    echo -ne "backing up config \r\n"
    LOGPATH="$LOGS_DIR"/config.$(date +'%Y-%m-%d').log
    mongodump -h "$CONFIG_BACKUP_NODE":"$CONFIG_PORT" --db config --out "$BACKUP_DIR" > "$LOGPATH" 2>&1
    tail -1 "$LOGPATH" | grep 'done dumping' &> /dev/null && STATE="Ok" || STATE="Config Backup Broken"

CheckState

echo -ne "creating archives \r\n"
for db in "${BACKUP_DBS_LIST[@]}"
    do
    tar -cf - "$BACKUP_DIR"/"$db" | lzop > "$BACKUP_DIR"/"$db".$(date +'%Y-%m-%d').tar.lzo
done

echo -ne "removing source files \r\n"
rm -r "$BACKUP_DIR"/{clickky,config}

echo -ne "clearing backups older that $BACKUP_STORE_DAYS days \r\n"
/usr/bin/find /backup/mongo/*.lzo -maxdepth 0 -mtime +"$BACKUP_STORE_DAYS" -delete
