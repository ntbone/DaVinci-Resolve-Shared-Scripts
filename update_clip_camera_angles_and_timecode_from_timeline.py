#from python_get_resolve import GetResolve
from timecode import Timecode
import inspect


def SetMediaPoolItemInOut(mediaPoolItem, startCode, endCode):
    if not mediaPoolItem.SetClipProperty('In', str(startCode)):
        print(f'Unable to set In  for "{mediaPoolItem.GetName()}"')
    if not mediaPoolItem.SetClipProperty('Out TC', str(endCode)):
        print(f'Unable to set Out for "{mediaPoolItem.GetName()}"')
    print("success")
    return 

def SetMediaPoolItemTimeCode(mediaPoolItem, startCode, endCode):
    if not mediaPoolItem.SetClipProperty('Start TC', str(startCode)):
        print(f'Unable to set start time code for "{mediaPoolItem.GetName()}"')
    #if not mediaPoolItem.SetClipProperty('End TC', str(endCode)):
    #    print(f'Unable to set end time code for "{mediaPoolItem.GetName()}"')
    return 

def TransferTimelineTimeCodeToMediaPoolItem(timeLineItem, frameRate, destinationMediaPoolItem):
    mediaPoolItem = timeLineItem.GetMediaPoolItem()
    print("    Found " + timeLineItem.GetName())
    print("    - Timeline references goes from frame ", timeLineItem.GetStart(), "to", timeLineItem.GetEnd(), "for", timeLineItem.GetDuration(), "frames.")
    #print("Media item ",  mediaPoolItem.GetName(), mediaPoolItem.GetMetadata())
    #print(mediaPoolItem.GetClipProperty())
    
    #currently this doens't work for audio items because they do not have frames.
    #----------------------------------------
    #framesProperty = mediaPoolItem.GetClipProperty('Frames')
    #if framesProperty is not None:
    #    mediaItemFrames = int(framesProperty)
    #    if timeLineItem.GetDuration() != mediaItemFrames:
    #        print("Clip has been cut on timeline. Durations do not match.", timeLineItem.GetDuration(), "!=", mediaItemFrames)
    #----------------------------------------

    startFrame = timeLineItem.GetStart()
    endFrame = timeLineItem.GetEnd() 

    startTimeCode = Timecode(frameRate) #, None, None, startFrame, )
    # timecode assumes frame 0 but Resolve assumes 1  Was uanble to set frame_number per Timecode documentation
    startTimeCode.frames = startFrame + 1
    endTimeCode = Timecode(frameRate)
    endTimeCode.frames = endFrame + 1

    print("    - Clip goes from", startTimeCode, "to", endTimeCode)
    SetMediaPoolItemTimeCode(destinationMediaPoolItem, startTimeCode, endTimeCode) 
    return


def DuplicateMediaPoolItem(mediaPoolItem):
    filePath = mediaPoolItem.GetClipProperty('File Path')
    importedItems = mediaPool.ImportMedia([filePath])

    if importedItems is None:
        return None
    return importedItems[0]


#if an invalid media pool item ends up as the first item in a track it causes the whole thing to error out both for dumping and creating the timecode.

def DumpTracks(trackType, visistedTrackItemFilePaths):
    trackCount = timeLine.GetTrackCount(trackType)
    for trackNumber in range(1, trackCount + 1):
        print(f"Track '{timeLine.GetTrackName(trackType, trackNumber)}' has")
        trackItems = timeLine.GetItemListInTrack(trackType, trackNumber)           
        for item in trackItems:
            mediaPoolItem = item.GetMediaPoolItem()           
            if mediaPoolItem is None:
                print("No media pool item found for ", item.GetName())
                return

            mediaPoolItemClipProperties = mediaPoolItem.GetClipProperty()

            #print(f"     MediaId = {mediaPoolItem.GetMediaId()}")
            #print(f"     MetaData = {mediaPoolItem.GetMetadata()}")
            #print(f"     ClipProperties = {mediaPoolItem.GetClipProperty()}")
            #modified = mediaPoolItem.GetClipProperty('Date Modified')
            #print(f"      Type = {type(modified)} Date Modified = {modified}")
            #if mediaPoolItem.SetClipProperty('Date Modified', 'Fri Sep 10 22:39:36 2021') is False:
            #    print("     Unable to set modified date")

            if mediaPoolItemClipProperties is None:
                print(f"   - No clip properties found for {mediaPoolItem.GetName()}")
                print(f"     MediaId = {mediaPoolItem.GetMediaId()}")
                print(f"     MetaData = {mediaPoolItem.GetMetadata()}")

                #metaData = mediaPoolItem.GetMetadata()                
                #if 'Frame Rate' in metaData:
                #    print(f"     Found 'Frame Rate' in metadata. Removing")
                #    #del metaData['Frame Rate']       
                #    del metaData['Production Name']
                #    metaData['Frame Rate'] = None                    
                #    print(f"     MetaData is now {metaData}")
                #    if mediaPoolItem.SetMetadata(metaData):
                #        print(f"     MetaData = {mediaPoolItem.GetMetadata()}")
                #    else:
                #        print("f     Unable to fix metadata")
                #    mediaPoolItem.SetMetadata('Frame Rate', '')
                #    mediaPoolItem.SetMetadata('Production Name', "This is a test")

                #    print(f"     MetaData = {mediaPoolItem.GetMetadata()}")
            else:
                if 'File Path' not in mediaPoolItemClipProperties:
                    print("  - No file path found", mediaPoolItem.GetClipProperty())
                else:
                    mediaPoolItemFilePath = mediaPoolItemClipProperties['File Path']

                    if mediaPoolItemFilePath in visistedTrackItemFilePaths:
                        print(f" - Skipping '{item.GetName()}'")       
                    else:
                        visistedTrackItemFilePaths[mediaPoolItemFilePath] = mediaPoolItem                
                        print(f" - '{item.GetName()}'")                               

def UpdateTimeCodeForTrack(mediaPool, timeLine, frameRate, destinationFolder, trackType, trackNumber, cameraNumber, processedClips):    
    items = timeLine.GetItemListInTrack(trackType, trackNumber)
    if items is None:
        print("No items found in track ", track, ' in timeLine "', timeLine.GetName(), '"')
        return

    subFolder = mediaPool.AddSubFolder(destinationFolder, timeLine.GetTrackName(trackType, trackNumber))
    currentFolder = mediaPool.GetCurrentFolder()
    mediaPool.SetCurrentFolder(subFolder)

    trackName = timeLine.GetTrackName(trackType, trackNumber)

    for item in items:
        if item.GetName() in processedClips.keys():
            print(f"'{item.GetName()}' already processed. Skipping.")
        else:
            processedClips[item.GetName()] = item
            newMediaPoolItem = DuplicateMediaPoolItem(item.GetMediaPoolItem())                       

            if newMediaPoolItem is None:
                print(f"Cannot duplicate media pool item for '{item.GetName()}'")
                newMediaPoolItem = item.GetMediaPoolItem()

            #print(newMediaPoolItem.GetClipProperty())
            TransferTimelineTimeCodeToMediaPoolItem(item, frameRate, newMediaPoolItem)
        
        
            #if newMediaPoolItem.SetClipProperty('Camera #', cameraNumber) == False:
            #    print("Cannot set 'Camera #'")
            #newMediaPoolItem.SetClipProperty('Camera', str(cameraNumber))
            #newMediaPoolItem.SetClipProperty('Angle', str(cameraNumber))
            #newMediaPoolItem.SetMetadata('Camera #', str(cameraNumber))
            newMediaPoolItem.SetClipProperty('Angle', trackName)
            newMediaPoolItem.SetMetadata('Camera #', trackName)

            #print(newMediaPoolItem.GetClipProperty())
        

    # probably shouldn't worry about setting this back.  
    mediaPool.SetCurrentFolder(currentFolder)
    return


def AddBaseImage(mediaPool, timeLine, frameRate):
    print("Importing base image")
    baseImageMediaPoolItem = mediaPool.ImportMedia(['V:/Recordings/2021/External/BaseImage.png'])[0]
    print("Base image imported")


    startFrame = timeLine.GetStartFrame()
    endFrame = timeLine.GetEndFrame()

    startTimeCode = Timecode(frameRate)
    startTimeCode.frames = startFrame + 1
    endTimeCode = Timecode(frameRate)
    endTimeCode.frames = endFrame + 1

    print("Base image goes from", startTimeCode, "to", endTimeCode)
    SetMediaPoolItemTimeCode(baseImageMediaPoolItem, startTimeCode, endTimeCode) 
    #SetMediaPoolItemInOut(baseImageMediaPoolItem, startTimeCode, endTimeCode) 

    return

def UpdateTimeCodeForTracks(mediaPool, timeLine, frameRate, destinationFolder, trackType, currentTrackCount, processedClips):
    trackCount = timeLine.GetTrackCount(trackType)

    for trackIndex in range(1, trackCount + 1):
        currentTrackCount = currentTrackCount + 1
        print(f'Processing track {currentTrackCount} - "{timeLine.GetTrackName(trackType, trackIndex)}", {trackType}')
        UpdateTimeCodeForTrack(mediaPool, timeLine, frameRate, destinationFolder, trackType, trackIndex, currentTrackCount, processedClips)

    return currentTrackCount
        

    


def SomethingElse(mediaPool, timeLine, frameRate, destinationFolder):   
    visistedTrackItemFilePaths = {}
    
    DumpTracks('video', visistedTrackItemFilePaths)
    DumpTracks('audio', visistedTrackItemFilePaths)   
    print('Done dumpping tracks')

    currentTrackCount = 0

    processedClips = {}
    currentTrackCount = UpdateTimeCodeForTracks(mediaPool, timeLine, frameRate, destinationFolder, 'video', currentTrackCount, processedClips)
    currentTrackCount = UpdateTimeCodeForTracks(mediaPool, timeLine, frameRate, destinationFolder, 'audio', currentTrackCount, processedClips)   
    print('Done updating timecode')

    
    return 

def SomeFunction(currentProject, mediaPool, timeLine, destinationFolder):
    frameRate = timeline.GetSetting('timelineFrameRate')
    print("Frame rate is ", frameRate)    

    if timeLine is not None:
        #AddBaseImage(mediaPool, timeLine, frameRate)
        SomethingElse(mediaPool, timeLine, frameRate, destinationFolder)
    else:
        print("No timeline to process")

def GetSubFolder(folder, subFolderName):
    subFolders = folder.GetSubFolderList()
    for subFolder in subFolders:
        if subFolder.GetName() == subFolderName:
            return subFolder
    return None

def AddUniqueFolder(folder, baseName):
    counter = 0  
    availableName = baseName
    existingAdjustedFolder = GetSubFolder(rootFolder, baseName)

    while existingAdjustedFolder != None:
        #print("Found %s.  Incrementing and trying something else" % existingAdjustedFolder )
        counter = counter + 1
        availableName = baseName + ' (%s)' % counter
        existingAdjustedFolder = GetSubFolder(rootFolder, availableName)
    
    return mediaPool.AddSubFolder(mediaPool.GetRootFolder(), availableName)


        

resolve = app.GetResolve()
projectManager = resolve.GetProjectManager()
currentProject = projectManager.GetCurrentProject()
mediaPool = currentProject.GetMediaPool()
rootFolder = mediaPool.GetRootFolder()
timeLine = currentProject.GetCurrentTimeline()

adjustedFolder = AddUniqueFolder(rootFolder, 'Adjusted TC for ' + timeLine.GetName())
SomeFunction(currentProject, mediaPool, timeLine, adjustedFolder)

#currentFolder = mediaPool.GetCurrentFolder()


#for item in currentFolder.GetClipList():
#    print("found ", item.GetName())
#    print(item.GetMetadata())
#    print(item.GetClipProperty())
#    print()

#    print(item.SetClipProperty('Description', "This is a test setting descritpion"))
#    #if not item.SetClipProperty('End', 300):
#    #    print(f'Cannot set "End" for "{item.GetName()}')


#    #if not item.SetClipProperty('Duration', 300):
#    #    print(f'Cannot set "End" for "{item.GetName()}')








# Not necessarily. TimelineItem has a GetMediaPoolItem()
def FindMediaPoolItem(mediaPool, name):
    return FindMediaPoolItem(mediaPool.GetRootFolder())

def FindMediaPoolItem(name, folder):
    clips = folder.GetClipList()

    for clip in clips:
        if clip.GetName() == name:
            return clip

    folders = folder.GetSubFolderList()
        
    for subFolder in folders:
        clip = FindMediaPoolItem(name, subFolder)
        if clip is not None:
            return clip
    
    return  None