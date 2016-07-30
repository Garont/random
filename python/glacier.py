#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3, re, subprocess, tarfile, os, shutil
from datetime import datetime as dt
from datetime import timedelta as td
from optparse import OptionParser
now = dt.now()

fullBackupFlag=False

#settings
#https://github.com/MoriTanosuke/glacieruploader
backupStoreDays=90
workDir = "/opt/backups/code/"
backupPath = "/opt/backups/temp/"
glacierAwsProp = "/root/.aws/aws.properties"
glacierEndpoint = "https://glacier.eu-central-1.amazonaws.com"
glacierVault = "ClickkyFrankfurtBackups"
s3Region = "eu-central-1"
s3Bucket = "clickkyfrankfurtbucket"
partsize = "4294967296"
makeTarDir = "/home"
# makeTarDir = "/tmp/test"
defLogPath = "/var/log/glacier/"
dateTimeNow = "{year:d}-{month:02d}-{day:02d}_{hour:02d}-{minute:02d}".format(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute)
glacierCommName = "glacier-" + dateTimeNow
s3CommName = "s3-" + dateTimeNow
glacierLogPath = defLogPath + glacierCommName + ".log"
s3LogPath = defLogPath + s3CommName + ".log"
pattern = re.compile(r"(INFO: Uploaded Archive ID: )(?P<archive_id>\S+)")
datePattern = re.compile(r"(\S+?)(?P<date_time>[0-9]{4}\-[0-9]{2}\-[0-9]{2}\_[0-9]{2}-[0-9]{2})(\S+)")
dbPath = workDir+"backups.db"
htmlPath = "/var/www/backups/index.html"
conn = sqlite3.connect(dbPath)
c = conn.cursor()
archiveName = glacierCommName + ".tar"
s3Archive = backupPath + s3CommName + ".tar.gz"
tarPath = backupPath + archiveName
#end settings




parser = OptionParser()
parser.add_option("-u", "--upload",
                  action="store_true", dest="glacier_Upload",
                  help="Default behaviour: Create archive, upload it to glacier, update sql file and upload it to S3 with logs. Generate html")
parser.add_option("-d", "--delete",
                  action="store_true", dest="glacier_Delete",
                  help="Default behaviour: Delete file from glacier. Update sql")
parser.add_option("-r", "--remove-old",
                  action="store_true", dest="remove_Old",
                  help="Delete files from glacier and s3 older than "+str(backupStoreDays) + " days or you can pass your num")

parser.add_option("-f", "--full_backup",
                  action="store_true", dest="full_Backup",
                  help="Making full backup with all by-mtime files")

try:
    (options, args) = parser.parse_args()
except:
    parser.print_help()
    exit(0)


backupsList = [
               {"backupsPath":"/home/confluenceback/backup",         "PostBackPath":"/home/confluenceback/glacier-processed/",            "bType":"by-file","sDays":""},
               {"backupsPath":"/home/drupalbak/backup",              "PostBackPath":"/home/drupalbak/glacier-processed/",                 "bType":"by-file","sDays":""},
               {"backupsPath":"/home/gitlabback/backup",             "PostBackPath":"/home/gitlabback/glacier-processed/",                "bType":"by-file","sDays":""},
               {"backupsPath":"/home/mongodump/backup",              "PostBackPath":"/home/mongodump/glacier-processed/",                 "bType":"by-file","sDays":""},
               {"backupsPath":"/home/mysqldumps/backup",             "PostBackPath":"/home/mysqldumps/glacier-processed/",                "bType":"by-file","sDays":""},
               {"backupsPath":"/home/red1/backups",                  "PostBackPath":"/home/red1/glacier-processed/",                      "bType":"by-file","sDays":""},
               {"backupsPath":"/home/stashback/backup",              "PostBackPath":"/home/stashback/glacier-processed/",                 "bType":"by-file","sDays":""},
               {"backupsPath":"/home/jirabackup/backup/jira/export", "PostBackPath":"/home/jirabackup/backup/jira/glacier-processed/",    "bType":"by-file","sDays":""},
               {"backupsPath":"/home/jirabackup/backup/testrail",    "PostBackPath":"/home/jirabackup/backup/testrail/glacier-processed/","bType":"by-file","sDays":""},
               {"backupsPath":"/home/ebk/backup",                    "PostBackPath":"/home/ebk/glacier-processed/",                       "bType":"by-file","sDays":""},


               {"backupsPath":"/home/jirabackup/backup/jira/attachments/", "PostBackPath":"","bType":"by-mtime","sDays":"8"},
               {"backupsPath":"/home/storagedump/files",                   "PostBackPath":"","bType":"by-mtime","sDays":"8"}
             ]


def createTar(filesArray, tarPath, mode="w"):
    tar = tarfile.open(tarPath, mode)

    try:
        for file in filesArray:
            backupsPath = file["backupsPath"]
            PostBackPath = file["PostBackPath"]
            bType = file["bType"]
            sDays = file["sDays"]

            #overriding type for full backup
            if fullBackupFlag:
                if bType == "by-mtime":
                    bType = "simple"

            if bType == "by-file":
                if not os.path.isdir(PostBackPath):
                    os.makedirs(PostBackPath)
                for root,dirs,files in os.walk(backupsPath):
                    for fname in files:
                        path = os.path.join(root,fname)
                        tar.add(path)
                        try:
                            shutil.move(path, PostBackPath)
                        except Exception as e:
                            print "Error: %s" % e

            elif bType == "by-mtime":
                ago = now - td(days = int(sDays))
                for root,dirs,files in os.walk(backupsPath):
                    for fname in files:
                        path = os.path.join(root,fname)
                        st = os.stat(path)
                        mtime = dt.fromtimestamp(st.st_mtime)
                        if mtime > ago:
                            tar.add(path)

            elif bType == "simple":
                tar.add(backupsPath)

            else:
                print "bType error. exiting"
                exit(1)

        tar.close()
    except Exception as e:
        print "archive %s creation error: %s. Exiting" % (tarPath, e)
        exit(1)

def logWriter(out, filePath):
    mode = 'a' if os.path.exists(filePath) else 'w+'
    logFile = open(filePath, mode)
    for line in out:
        logFile.write(str(line)+"\r\n")
    logFile.close()

def updateDBFromLog(log):
    IDFound = False
    for line in open(log, 'r'):
        result=pattern.match(line)
        if result:
            archiveID = result.group('archive_id')
	    print archiveName, archiveID
            c.execute("INSERT INTO backups VALUES (?,?)", (archiveName, archiveID,))
            conn.commit()
	    print "ArchiveID found %s" % archiveID
            IDFound = True
    if not IDFound:
        print "ArchiveID Not Found"
        exit(1)

def s3(operation, *args, **kwargs):
    s3file = kwargs.get('s3file', None)

    basicCall = "java -jar " + workDir + "AmazonS3-1.0-SNAPSHOT-jar-with-dependencies.jar --region " + s3Region + " --bucket " + s3Bucket

    if operation == "upload":
        try:
            out = filter(None, subprocess.check_output( basicCall + " --upload --file " + s3file + " --destination-path " + s3file.split("/")[-1:][0], stderr=subprocess.STDOUT, shell=True )).split("\n")
            print out
            logWriter(out, s3LogPath)
        except Exception as e:
            logWriter(e, s3LogPath)
            print "S3 upload failed:, %s" % e

    if operation == "list":
        try:
            out = filter(None, subprocess.check_output( basicCall + " --list", stderr=subprocess.STDOUT, shell=True ).split("\n"))
            return out
        except Exception as e:
            print "S3 list failed:, %s" % e

    if operation == "delete":
        try:
            out = filter(None, subprocess.check_output( basicCall + " --delete --file " + s3file, stderr=subprocess.STDOUT, shell=True )).split("\n")
            logWriter(out, s3LogPath)
            print out
        except Exception as e:
            logWriter(e, s3LogPath)
            print "S3 deleting failed:, %s" % e



def glacier(operation, *args, **kwargs):
    glfile = kwargs.get('glfile', None)
    basicCall = "java -jar " + workDir + "uploader.jar --credentials " + glacierAwsProp + " --endpoint " + glacierEndpoint + " --vault " + glacierVault

    if operation == "upload":
        print "Glacier Upload called"
        createTar(backupsList, tarPath)
        try:
            out = filter(None, subprocess.check_output( basicCall + " --multipartupload " + tarPath + " --partsize " + partsize, stderr=subprocess.STDOUT, shell=True )).split("\n")
            print out
            logWriter(out, glacierLogPath)
            os.remove(tarPath)
        except Exception as e:
            logWriter(e, glacierLogPath)
            print "upload to glacier failed: %s. Exiting" % e
            exit(1)

        updateDBFromLog(glacierLogPath)

        backList = [{"backupsPath":dbPath,"PostBackPath":"","bType":"simple","sDays":""},
                    {"backupsPath":glacierLogPath,"PostBackPath":"","bType":"simple","sDays":"10"}
                    ]
        createTar(backList, s3Archive, mode = "w:gz")
        s3("upload", s3file = s3Archive)
        os.remove(s3Archive)

    if operation == "delete":
        print "Glacier Delete called"
        try:
            out = filter(None, subprocess.check_output( basicCall + " --delete " + glfile, stderr=subprocess.STDOUT, shell=True)).split("\n")
            print out
            logWriter(out,glacierLogPath)
        except Exception as e:
            logWriter(e,glacierLogPath)
            print "Deleting from glacier failed: %s. Exiting" % e
            exit(1)

        c.execute("DELETE FROM backups WHERE hash=?", (glfile,))
        conn.commit()
        backList = [{"backupsPath":dbPath,"PostBackPath":"","bType":"simple","sDays":""},
                    {"backupsPath":glacierLogPath,"PostBackPath":"","bType":"simple","sDays":"10"}
                    ]
        createTar(backList, s3Archive)
        s3("upload", s3file = s3Archive)
        os.remove(s3Archive)


def isTooOld(arr, bType, bsd):
    backupStoreSeconds = bsd * 86400.0
    if not arr:
        print "no files found in {0} array".format(bType)
        exit(0)
    for file in arr:
        result = datePattern.match(file.split("/")[-1:][0].split(";")[0])
        if result:
            date_time = result.group('date_time')
            archive_time = (now - dt.strptime(date_time,"%Y-%m-%d_%H-%M")).total_seconds()
            if archive_time > backupStoreSeconds:
                print "{0} is older than {1} days: ({2:.01f}). Deleting".format(file, bsd,(archive_time / 86400.0))
                if bType == "s3":
                    file = file.split(";")[0]
                    s3("delete", s3file=file)
                elif bType == "glacier":
                    sql = c.execute("SELECT hash FROM backups WHERE archive LIKE ?", ("%" + file + "%",))
                    hash = [row[0] for row in sql][0]
                    glacier("delete", glfile = hash)
                else:
                    print "wrong request (file:{0}, bType:{1}). Exiting".format(file, bType)
                    exit(1)
            else:
                print "{0} will be alive {1:.1f} days more".format(file, (backupStoreSeconds - archive_time) / 86400.0)

def removeOld(*args,**kwargs):
    bsd = args[0] if args else backupStoreDays
    try:
        bsd = int(bsd)
    except Exception as e:
        print "must provide integer value"
        exit(1)
    print "deleting from glacier and s3 archives that older than %s days" % bsd
    #processing s3
    s3files = s3("list")
    isTooOld(s3files, "s3", bsd)
    #processing glacier
    isTooOld([row[0] for row in c.execute("SELECT archive FROM backups")], "glacier", bsd)


#argparser caller
if options.full_Backup:
    fullBackupFlag=True
    archiveName = glacierCommName + "_full.tar"
    tarPath = backupPath + archiveName
if options.glacier_Delete:
    glacier("delete", glfile = args[0])
if options.glacier_Upload:
    glacier("upload")
if options.remove_Old:
    if args:
        removeOld(args[0])
    else:
        removeOld()
#end argparser caller


#createhtml
ret=[]
for row in c.execute("SELECT * FROM backups"):
    ret.append(row)
conn.close()

htmlFile = open(htmlPath, "w+")

htmlFile.write("""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>glacier</title>
        </head>
        <body>""")

htmlFile.write("\n<h1>Glacier Archive List</h1>")

htmlFile.write("<ol>")
for i in ret:
    htmlFile.write("\n<li><p>{0}, {1}</p></li>".format(i[0], i[1]))
htmlFile.write("</ol>")

htmlFile.write("""\n</body>
        </html>""")
htmlFile.close()

#end createhtml
