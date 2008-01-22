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
    # Tracker
    {'Name':"Threshold", 
     'path':"/trackerconfig/tracker/track/threshold/@value", 
     'min':1, 'max':255, 'increment':1, 'precision':0},
    {'Name':"Min Area", 
     'path':"/trackerconfig/tracker/track/areabounds/@min", 
     'min':1, 'max':1000000, 'increment':3, 'precision':0},
    {'Name':"Max Area", 
     'path':"/trackerconfig/tracker/track/areabounds/@max", 
     'min':20, 'max':1000000, 'increment':10, 'precision':0},
    {'Name':"Contour Precision", 
     'path':"/trackerconfig/tracker/contourprecision/@value", 
     'min':0, 'max':1000, 'increment':1, 'precision':0},

    # Camera
    {'Name':"Brightness", 
     'path':"/trackerconfig/camera/brightness/@value", 
     'min':128, 'max':383, 'increment':1, 'precision':0},
    {'Name':"Exposure", 
     'path':"/trackerconfig/camera/exposure/@value", 
     'min':0, 'max':511, 'increment':1, 'precision':0},
    {'Name':"Shutter", 
     'path':"/trackerconfig/camera/shutter/@value", 
     'min':0, 'max':7, 'increment':1, 'precision':0},
    {'Name':"Gain", 
     'path':"/trackerconfig/camera/gain/@value", 
     'min':0, 'max':255, 'increment':1, 'precision':0},

    # Transform
    {'Name':"Displacement x", 
     'path':"/trackerconfig/transform/displaydisplacement/@x", 
     'min':-5000, 'max':0, 'increment':1, 'precision':0},
    {'Name':"y", 
     'path':"/trackerconfig/transform/displaydisplacement/@y", 
     'min':-5000, 'max':0, 'increment':1, 'precision':0},
    {'Name':"Scale x", 
     'path':"/trackerconfig/transform/displayscale/@x", 
     'min':-3, 'max':3, 'increment':0.01, 'precision':2},
    {'Name':"y", 
     'path':"/trackerconfig/transform/displayscale/@y", 
     'min':-3, 'max':3, 'increment':0.01, 'precision':2},
    {'Name':"Distortion p2", 
     'path':"/trackerconfig/transform/distortionparams/@p2", 
     'min':-3, 'max':3, 'increment':0.0000001, 'precision':7},
    {'Name':"p3", 
     'path':"/trackerconfig/transform/distortionparams/@p3", 
     'min':-3, 'max':3, 'increment':0.0000001, 'precision':7},
    {'Name':"Trapezoid", 
     'path':"/trackerconfig/transform/trapezoid/@value", 
     'min':-3, 'max':3, 'increment':0.00001, 'precision':5},
    {'Name':"Angle", 
     'path':"/trackerconfig/transform/angle/@value", 
     'min':-3.15, 'max':3.15, 'increment':0.01, 'precision':2},
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

    try:
        if Event.type == avg.CURSORDOWN:
            Type = "c"
        elif Event.type == avg.CURSORUP:
            Type = "d"
        elif Event.type == avg.CURSORMOTION:
            Type = "m"
        else:
            print Event.type

        if Event.source == avg.TRACK:

            posMsg = OSC.Message()
            posMsg.setAddress('/b/'+Type)
            posMsg.append(Event.cursorid)
            posMsg.append(int(Event.center[0]))
            posMsg.append(int(Event.center[1]))
            
            if sendContour and Type != 'd':
                bundle = OSC.Bundle()
                bundle.append(posMsg)
                
                contour = Event.getContour()

                # This triggers contour reset on server side
                rstMsg = OSC.Message()
                rstMsg.setAddress('/b/r')
                rstMsg.append(Event.cursorid)
                rstMsg.append(len(contour))
                
                bundle.append(rstMsg)
              
                i = 0
                contMsg = OSC.Message()
                for point in contour:
                    contMsg.clear()
                    contMsg.setAddress('/b/v')
                    contMsg.append(Event.cursorid)
                    contMsg.append(point[0])
                    contMsg.append(point[1])
                    contMsg.append(i)

                    bundle.append(contMsg)
                    i = i+1
                                    
                OSCClient.sendRawMessage(bundle.getRawMessage())

            else:
                OSCClient.sendMessage(posMsg)
    except socket.error, e:
        print e
#        print "EVENT="+Type+" ID="+str(Event.cursorid)+" POS="+str(Event.x)+","+str(Event.y)+" AREA="+str(Event.area)

def changeParam(Change):
    global curParam
    global paramList
    param = paramList[curParam]
    if param['increment'] >= 1:
        Val = int(Tracker.getParam(param['path']))
    else:
        Val = float(Tracker.getParam(param['path']))
    Val += Change*param['increment']
    if Val < param['min']:
        Val = param['min']
    if Val > param['max']:
        Val = param['max']
    Tracker.setParam(param['path'], str(Val))
    
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
            
def onKeyUp(Event):
    global Tracker
    global showImage
    global curParam
    global saveIndex
    global paramList
    if Event.keystring == "1":
        showImage = not(showImage)
        Tracker.setDebugImages(showImage, showImage)
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
    displayParams()

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
    global Tracker
    global showImage
    global MidiIn
    if showImage:
        showTrackerImage(avg.IMG_DISTORTED, "distorted", 960, 720)
        showTrackerImage(avg.IMG_FINGERS, "fingers", 960, 720)
        showTrackerImage(avg.IMG_CAMERA, "camera", 160, 120)
        showTrackerImage(avg.IMG_NOHISTORY, "nohistory", 160, 120)
        showTrackerImage(avg.IMG_HISTOGRAM, "histogram", 160, 120)
    fps = Player.getEffectiveFramerate()
    Player.getElementByID("fps").text = '%(val).2f' % {'val': fps} 

#        flipBitmap(Node)

#    while MidiIn.Poll():
#        MidiData = MidiIn.Read(1) # read only 1 message at a time
#        Tracker.setParam("/trackerconfig/camera/brightness/@value",str(MidiData[0][0][2]*5))
#        print "Got message :",MidiData[0][0][0]," ",MidiData[0][0][1]," ",MidiData[0][0][2], MidiData[0][0][3]
#        print "VALUE=",MidiData[0][0][2]

value = 0
Player = avg.Player()
Log = avg.Logger.get()
Player.setResolution(0, 800, 0, 0) 
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
Player.setFramerate(60)
Tracker = Player.addTracker()
Tracker.setDebugImages(True, True)

showImage = True
Tracker.setDebugImages(True, True)

#OSCClient = OSC.Client("194.95.203.37", 12000)
OSCClient = OSC.Client("127.0.0.1", 12000)

Bitmap = Tracker.getImage(avg.IMG_CAMERA)

initMsg = OSC.Message()
initMsg.setAddress('/stage/init')
initMsg.append(Bitmap.getSize()[0])
initMsg.append(Bitmap.getSize()[1])
OSCClient.sendMessage(initMsg);

Player.setOnFrameHandler(onFrame)
displayParams()

#PrintDevices(INPUT)
#MidiIn = pypm.Input(5)

Player.play()

