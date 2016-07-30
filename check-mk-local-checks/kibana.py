#!/usr/bin/env python
import datetime
import pycurl
from elasticsearch import Elasticsearch

maxDelay=600.0
url="http://localhost:5601/app/kibana#"

def printer(status, text):
    print "%s Kibana_Status stat=%s;0;0 %s" % (status, status, text)

#check last elasticsearch record
currentTime = datetime.datetime.now()
client = Elasticsearch(["kibana-host.example.com", "kibana-host3.example.com"])

try:
    response = client.search(
        index="ls-"+currentTime.strftime("%Y.%m.%d"),
        body={ "query": { "match_all": {} }, "size":1, "sort": [{"@timestamp": {"order": "desc"}}]}
)
except:
    printer("2", "error connecting to elasticsearch")
    exit(2)


rsTime = response['hits']['hits'][0]['_source']['@timestamp']

tf = datetime.datetime.strptime(rsTime, "%Y-%m-%dT%H:%M:%S.000Z")
#tf = datetime.datetime.strptime("2016-01-25T13:35:26.000Z", "%Y-%m-%dT%H:%M:%S.000Z") #for test
timeDelta = (currentTime - tf).total_seconds()

if timeDelta > maxDelay:
    printer("2", "time delay is too big: "+str(time_delta)+" secs")
    exit(1)

#end elasticsearch checks

#check main page
class Storage:
    def __init__(self):
        self.contents = []

    def store(self, buf):
        self.contents.append(buf)

    def ret(self):
        return self.contents

retrieved_body = Storage()
retrieved_headers = Storage()
c = pycurl.Curl()

try:
    c.setopt(pycurl.CONNECTTIMEOUT, 5)
    c.setopt(pycurl.TIMEOUT, 5)
    c.setopt(pycurl.NOSIGNAL, 1)
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, retrieved_body.store)
    c.setopt(c.HEADERFUNCTION, retrieved_headers.store)
    c.perform()
    c.close()
except:
    printer("2", "Curl Connection exception")
    exit(2)

if retrieved_headers.ret()[0] != 'HTTP/1.1 200 OK\r\n':
    printer("2", "Invalid kibana response: "+retrieved_headers.ret()[0])
    exit(2)
#end check main page

printer("0", "Everything_Fine")
exit(0)
