import os.path, time, shutil
from pathlib import Path
from datetime import datetime
import hashlib
from PIL import Image

def LogInfo(content):
    # print("log: {}".format(content))
    log = open("SortLog.txt", "a+")
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
    print("Starting")
    LogInfo("starting")
    startingDir = '\Compare'
    finishedDir = '\Organized'

    FileFormats = {
        "PhotosAndVids": (".jpg", ".png", "mp4", ".m4v", ".gif", ".mod", ".moi", ".amr", ".bmp", ".cr2", ".mov", ".tif", ".avi", ".jpeg", ".wav", ".3gp"),
        "Photoshop": (".psd", ".pdd" ),
        "Passwords":  (".kdbx", ".key"),
        "Documents": (".zip", ".txt", ".pdf", ".docx", ".gdoc", ".csv", ".xlsx", ".xlsm", ".xml", "pptx"),
        "Music": (".mp3", ".flac", ".wma"),
        "Programming": (".java", ".class", ".sql", ".html", ".css", ".php", ".py"),
        "Programs": (".exe", ".bat", ".msi"),
        "Ebooks": (".epub", ".mobi")
    }
    fileFormats = []
    path = os.getcwd()
    startingDir = path + startingDir
    finishedDir = path + finishedDir
    for subdir, dirs, files in os.walk(startingDir):
        print("scanning directory {}".format(subdir))
        LogInfo("Scanning: {}".format(subdir))
        for file in files:
            try:
                formatExists = False
                #saves the formats moved to see if there are any missed ones
                oldFilePath = subdir + os.sep + file
                fileFormat = file.split('.')[-1]
                if fileFormat not in fileFormats:
                    fileFormats.append(fileFormat)
                #file info
                try:
                    stdfmt = '%Y:%m:%d %H:%M:%S'
                    with Image.open(oldFilePath) as exif:
                        info = exif._getexif()
                        #36867 is date taken
                        dateTaken = info[36867].split(" ",1)
                        modTime = datetime.strptime(info[36867], stdfmt)
                        modYear = modTime.year
                        modMonth = modTime.month

                except Exception as e:
                    modTime = time.localtime(os.path.getmtime(oldFilePath))
                    modYear = time.strftime('%Y', modTime)
                    modMonth = time.strftime('%m', modTime)

                for key in FileFormats:
                    if file.lower().endswith(tuple(FileFormats.get(key))):
                        if key == 'PhotosAndVids':
                            modMonth = modMonth.zfill(2)
                            newDirectory = "{}\\{}\\{}\\{}{}".format(finishedDir, key, modYear, modYear, modMonth)
                        else:
                            newDirectory = "{}\\{}\\{}".format(finishedDir, key, modYear)
                        #parents = true #makes new sub dir as needed exist_ok = True = ignore directory exist error
                        #check to see if file exists
                        Path(newDirectory).mkdir(parents=True, exist_ok=True)
                        newFilePath = "{}\{}".format(newDirectory, file)
                        MoveFile(oldFilePath, newFilePath, 0)
                        #the file has been moved so no need to sort through the rest of the keys
                        formatExists = True
                        break
                if not formatExists:
                    try:
                        newDirectory = "{}\\{}\\{}".format(finishedDir, "Unknown", modYear)
                        Path(newDirectory).mkdir(parents=True, exist_ok=True)
                        newFilePath = "{}\{}".format(newDirectory, file)
                        MoveFile(oldFilePath, newFilePath, 0)
                        LogInfo("Unknown Format: {}".format(oldFilePath))
                    except Exception as e:
                        LogInfo("Error: {} moving to {}".format(oldFilePath,newFilePath))
            except Exception as e:
                newDirectory = "{}\\{}\\{}".format(finishedDir, "Error", modYear)
                Path(newDirectory).mkdir(parents=True, exist_ok=True)
                newFilePath = "{}\{}".format(newDirectory, file)
                MoveFile(oldFilePath, newFilePath, 0)
                LogInfo("Error Format: {}".format(oldFilePath))
    LogInfo("Formats {} ".format(fileFormats))
    print("Finished")
except Exception as e:
    print(e)
