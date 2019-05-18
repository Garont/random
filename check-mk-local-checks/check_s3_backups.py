#!/usr/bin/env python

from boto.s3.connection import S3Connection
from datetime import datetime

LIMIT=90000
BUCKETS={"xxx-backups":"pg-%Y%m%d_%H%M%S.tar.bz2"}
S3LOGIN="AKIAPPPPPPPSSSSSSS"
S3PASS="XXXXXXXXXXXXXXXXXXXXXXXXXX"
S3HOST="s3.ap-northeast-2.amazonaws.com"

try:
    conn = S3Connection(S3LOGIN, S3PASS, host=S3HOST)
except Exception as e:
    for BUCK, FORMAT in BUCKETS.iteritems():
        print "2 {bucket}_BACKUPS count={dts};0;0;0; SCRIPT ERROR {e}".format(bucket=BUCK, dts=0, limit=0, e=e)

for BUCK, FORMAT in BUCKETS.iteritems():
    try:
        bucket = conn.get_bucket(BUCK)
        last_dump = [x.key for x in bucket.get_all_keys()][-1]
        if last_dump == 'privkey.txt':
            last_dump=[x.key for x in bucket.get_all_keys()][:-1][-1] #cut last and try again
        dump_date = datetime.strptime(last_dump, FORMAT)
        now = datetime.now()
        delta = now - dump_date

        if delta.total_seconds() < LIMIT:
            print "0 {bucket}_BACKUPS count={dts};0;0;0; OK".format(bucket=BUCK, dts=int(delta.total_seconds()))
        else:
           print "2 {bucket}_BACKUPS count={dts};0;0;0; BACKUPS OLDER THAN {limit}".format(bucket=BUCK, dts=int(delta.total_seconds()), limit=LIMIT)
    except Exception as e:
           print "2 {bucket}_BACKUPS count={dts};0;0;0; SCRIPT ERROR {e}".format(bucket=BUCK, dts=0, limit=0, e=e)
