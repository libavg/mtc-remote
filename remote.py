#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from libavg import avg
import OSC
import socket
#import pypm

INPUT=0
OUTPUT=1

paramList = [
    {'Name':"Track Threshold", 
     'path':"/trackerconfig/tracker/track/threshold/@value", 
     'min':1, 'max':255, 'increment':1, 'precision':0},
    {'Name':"Brightness", 
     'path':"/trackerconfig/camera/brightness/@value", 
     'min':1, 'max':255, 'increment':1, 'precision':0},
    {'Name':"Shutter", 
     'path':"/trackerconfig/camera/shutter/@value", 
     'min':1, 'max':533, 'increment':1, 'precision':0},
    {'Name':"Gain", 
     'path':"/trackerconfig/camera/gain/@value", 
     'min':16, 'max':64, 'increment':1, 'precision':0},
]

sendContour=1
curParam=0

def PrintDevices(InOrOut):
    print
    print 'MIDI INPUT DEVICES:'
    for loop in range(pypm.CountDevices()):
        interf,name,inp,outp,opened = pypm.GetDeviceInfo(loop)
        if ((InOrOut == INPUT) & (inp == 1) |
            (InOrOut == OUTPUT) & (outp ==1)):
            print loop, name," ",
            if (inp == 1): print "(input) ",
            else: print "(output) ",
            if (opened == 1): print "(opened)"
            else: print "(unopened)"
    print

def onTouch(Event):
    global OSCClient
    global sendContour

    if Event.type == avg.CURSORDOWN:
        Type = "created"
    elif Event.type == avg.CURSORUP:
        Type = "destroyed"
    elif Event.type == avg.CURSORMOTION:
        Type = "motion"
    else:
        print Event.type

    if Event.source == avg.TRACK:

        posMsg = OSC.Message()
        posMsg.setAddress('/blob/'+Type)
        posMsg.append(Event.cursorid)
        posMsg.append(Event.x)
        posMsg.append(Event.y)
        
        if sendContour and Type != 'destroyed':
            bundle = OSC.Bundle()
            bundle.append(posMsg)
            
            contour = Event.getContour()

            # This triggers contour reset on server side
            rstMsg = OSC.Message()
            rstMsg.setAddress('/blob/rstc')
            rstMsg.append(Event.cursorid)
            rstMsg.append(len(contour))
            
            bundle.append(rstMsg)
          
            i = 0
            contMsg = OSC.Message()
            for point in contour:
                contMsg.clear()
                contMsg.setAddress('/blob/cv')
                contMsg.append(Event.cursorid)
                contMsg.append(point[0])
                contMsg.append(point[1])
                contMsg.append(i)

                bundle.append(contMsg)
                i = i+1
		        		        
            OSCClient.sendRawMessage(bundle.getRawMessage())

        else:
            OSCClient.sendMessage(posMsg)

#        print "EVENT="+Type+" ID="+str(Event.cursorid)+" POS="+str(Event.x)+","+str(Event.y)+" AREA="+str(Event.area)

    elif Event.source == avg.MOUSE:
        Source = "/mouse/"

def changeParam(Change):
    global curParam
    global paramList
    param = paramList[curParam]
    Val = int(Tracker.getParam(param['path']))
    Val += Change*param['increment']
    if Val < param['min']:
        Val = param['min']
    if Val > param['max']:
        Val = param['max']
    Tracker.setParam(param['path'], str(Val))

def onKeyUp(Event):
    global Tracker
    global showImage
    global curParam
    global saveIndex
    global paramList
    if Event.keystring == "1":
        showImage = not(showImage)
    elif Event.keystring == "h":
        Tracker.resetHistory()
        print "History reset"
    elif Event.keystring == "up":
        if curParam > 0:
            curParam -= 1
    elif Event.keystring == "down":
        if curParam < len(paramList)-1:
            curParam += 1
    elif Event.keystring == "left":
        changeParam(-1)
    elif Event.keystring == "right":
        changeParam(1)
    elif Event.keystring == "page up":
        changeParam(-10)
    elif Event.keystring == "page down":
        changeParam(10)
    elif Event.keystring == "h":
        Tracker.resetHistory()
        print "History reset"
    elif Event.keystring == "s":
        Tracker.saveConfig()
        print ("Tracker configuration saved.")
    elif Event.keystring == "w":
        saveIndex += 1
        Tracker.getImage(avg.IMG_CAMERA).save("img"+str(saveIndex)+"_camera.png")
        Tracker.getImage(avg.IMG_DISTORTED).save("img"+str(saveIndex)+"_distorted.png")
        Tracker.getImage(avg.IMG_NOHISTORY).save("img"+str(saveIndex)+"_nohistory.png")
        Tracker.getImage(avg.IMG_HIGHPASS).save("img"+str(saveIndex)+"_highpass.png")
        Tracker.getImage(avg.IMG_FINGERS).save("img"+str(saveIndex)+"_fingers.png")
        print ("Images saved.")

def flipBitmap(Node):
    Grid = Node.getOrigVertexCoords()
    Grid = [ [ (pos[0], 1-pos[1]) for pos in line ] for line in Grid]
    Node.setWarpedVertexCoords(Grid)

def onFrame():
    def showTrackerImage(TrackerImageID, NodeID, w, h):
        Bitmap = Tracker.getImage(TrackerImageID)
        Node = Player.getElementByID(NodeID)
        Node.setBitmap(Bitmap)
        Node.width=w
        Node.height=h
    def displayParams():
        global paramList
        global curParam
        i = 0
        for Param in paramList:
            Node = Player.getElementByID("param"+str(i))
            Path = Param['path']
            Val = float(Tracker.getParam(Path))
            Node.text = Param['Name']+": "+('%(val).'+str(Param['precision'])+'f') % {'val': Val}
            if curParam == i:
                Node.color = "FFFFFF"
            else:
                Node.color = "A0A0FF"
            i += 1 
    global Tracker
    global showImage
    global MidiIn
    if showImage:
        showTrackerImage(avg.IMG_DISTORTED, "distorted", 960, 720)
        showTrackerImage(avg.IMG_FINGERS, "fingers", 960, 720)
        showTrackerImage(avg.IMG_CAMERA, "camera", 160, 120)
        showTrackerImage(avg.IMG_NOHISTORY, "nohistory", 160, 120)
        showTrackerImage(avg.IMG_HISTOGRAM, "histogram", 160, 120)
    displayParams()

#        flipBitmap(Node)

#    while MidiIn.Poll():
#        MidiData = MidiIn.Read(1) # read only 1 message at a time
#        Tracker.setParam("/trackerconfig/camera/brightness/@value",str(MidiData[0][0][2]*5))
#        print "Got message :",MidiData[0][0][0]," ",MidiData[0][0][1]," ",MidiData[0][0][2], MidiData[0][0][3]
#        print "VALUE=",MidiData[0][0][2]

def testParam():
    global value
    Tracker.setParam("/trackerconfig/camera/brightness/@value",str(value))
    value=value+1

    if (value > 500): value = 0
#    Tracker.saveConfig()
    print Tracker.getParam("/trackerconfig/camera/brightness/@value")

value = 0
Player = avg.Player()
Log = avg.Logger.get()
#Player.setResolution(0, 960, 0, 0) 
#Player.setResolution(1, 0, 0, 0) 
Log.setCategories(Log.APP |
                  Log.WARNING | 
                  Log.PROFILE |
                  Log.CONFIG
#                  Log.EVENTS |
#                  Log.EVENTS2
#                  Log.PROFILE_LATEFRAMES
                 )
Player.loadFile("remote.avg")
Player.setFramerate(20)
Tracker = Player.addTracker()
Tracker.setDebugImages(True, True)

showImage = True
Tracker.setDebugImages(True, True)

OSCClient = OSC.Client("194.95.203.162", 12000)
Player.setOnFrameHandler(onFrame)

#PrintDevices(INPUT)
#MidiIn = pypm.Input(5)

Player.play()

