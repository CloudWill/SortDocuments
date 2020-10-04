import os.path, time, shutil
from pathlib import Path
from datetime import datetime
import hashlib
from PIL import Image

def LogInfo(content):
    # print("log: {}".format(content))
    log = open("UndoLog.txt", "a+")
    log.write("{} : {}\n".format(datetime.now(), content))
    log.close()

def Md5(fname):
    hash_md5 = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def Md5Compare(oldPath, newPath):
    return Md5(oldPath) == Md5(newPath)

def MoveFile(oldPath, newPath, count):
    fileName = newPath.split('.')
    fileExtention = fileName[-1]
    fileWPath = newPath[:-len(fileExtention)]
    if count != 0:
        newPath = "{}-{}.{}".format(fileWPath, count, fileExtention)
    if os.path.exists(newPath):
        if Md5Compare(oldPath, newPath):
            LogInfo("Not Moved: {} same as {}".format(oldPath, newPath))
        else:
            count +=1
            #recursion to see if there are different files with the same name but different md5
            MoveFile(oldPath, newPath, count)
    else:
        LogInfo("Moved: {} moved to {}".format(oldPath, newPath))
        shutil.move(oldPath, newPath)

try:

    # Using readlines()
    file1 = open('undo.txt', 'r')
    Lines = file1.readlines()

    count = 0
    # Strips the newline character
    for line in Lines:
        a = line.find('Moved:')
        b = line.find('moved to')
        #find returns -1 if string not found
        if a != -1 and b != -1 :
            oldDirectory = line[a+7:b]
            newDirectory = line[b+9:-1]
            try:
                LogInfo("Moved: {} moved to {}".format(newDirectory, oldDirectory))
                shutil.move(newDirectory, oldDirectory)
            except Exception as e:
                LogInfo("Directory {} dne".format(newDirectory))
    print("Finished")
except Exception as e:
    print(e)
