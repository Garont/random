#!/bin/bash

unset repstatus
declare -A repstatus

while read line ; do
	k="$(echo $line | awk '{print $1}')"
	v="$(echo $line | awk '{print $3}')"
	if [ -z "$k" ] ; then echo "2 REPLICATION count=2;0;0;0; Missing replication subscribers" && exit 0 ; fi
	repstatus["$k"]="$v"
done < <(sudo -u postgres -H psql -x  -c "select client_addr, state from pg_stat_replication;" | tail -n +2| sed  '/^$/d')

if [[ "${repstatus[client_addr]}" != "10.10.2.11" ]] ; then
 echo "2 REPLICATION count=2;0;0;0; Client missing repstatus[client_addr]"
 exit 0
fi

if [[ "${repstatus[state]}" != "streaming" ]] ; then
 echo "2 REPLICATION count=2;0;0;0; Replication state missing repstatus[state]"
 exit 0
fi

echo "0 REPLICATION count=0;0;0;0; Ok"
exit 0
