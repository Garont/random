#!/usr/bin/env python

import subprocess, smtplib
from time import gmtime, strftime
from email.mime.text import MIMEText

rs1List = ["bigmongo1.example.com:27017", "bigmongo2.example.com:27017", "mongodump.example.com:27117"]
rs2List = ["bigmongo4.example.com:27017", "bigmongo3.example.com:27017", "mongodump.example.com:27118"]
validAns = ["ARBITER", "SECONDARY", "PRIMARY"]

rsPorts = ["27117", "27118"]

def printer(status, text):
    print "%s Mongo_RS_Status stat=%s;0;0 %s" % (status, status, text)

def checker(replica, out, rslist, rs):
    noRoleArr=[]
    for i in out:
        noRoleArr.append(i.split(' ')[0])
    for outServ, sServ in zip(out, rslist):
            if not any(status in outServ for status in validAns):
                printer("2", rs+"_Server_Bad_Status:_"+outServ)
                exit(2)
            if sServ not in noRoleArr:
                printer("2", rs+"_Server_Missing:_"+sServ)
                exit(2)

for replica in rsPorts:
    out = filter(None, subprocess.check_output("mongo localhost:" + replica + "/clickky --eval 'printjson(rs.status().members.forEach(function(mem) { print (mem.name+\" \"+mem.stateStr); }));' | grep -v 'MongoDB\|connecting to\|undefined'", stderr=subprocess.STDOUT, shell=True)).split("\n")
    if replica == rsPorts[0]:
        checker(replica, out, rs1List, "rs1")
    else:
        checker(replica, out, rs2List, "rs2")

printer("0", "Everything_Fine")
exit(0)
