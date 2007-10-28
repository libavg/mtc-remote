#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from libavg import avg
import OSC
import controller
import socket

def onTouch(Event):
    global OSCController
    global HOST
    global PORT
    if Event.source != avg.TRACK:
        if Event.type == avg.CURSORDOWN:
            Type = "down"
        elif Event.type == avg.CURSORUP:
            Type = "up"
        elif Event.type == avg.CURSORMOTION:
            Type = "motion"
        else:
            print Event.type
        if OSCController:
            OSCController.sendMsg('/touch/'+Type, int(Event.cursorid), 
                    float(Event.x), float(Event.y))

def onKeyUp(Event):
    if Event.keystring == "s":
        Tracker.saveConfig()
        print ("Tracker configuration saved.")

def flipBitmap(Node):
    Grid = Node.getOrigVertexCoords()
    Grid = [ [ (pos[0], 1-pos[1]) for pos in line ] for line in Grid]
    Node.setWarpedVertexCoords(Grid)

def onFrame():
    global Tracker
    Bitmap = Tracker.getImage(avg.IMG_FINGERS)
    Node = Player.getElementByID("fingers")
    Node.setBitmap(Bitmap)
    Node.width=1280
    Node.height=720
    flipBitmap(Node)

Player = avg.Player()
Log = avg.Logger.get()
Player.setResolution(0, 640, 0, 0) 
#Player.setResolution(1, 0, 0, 0) 
Log.setCategories(Log.APP |
                  Log.WARNING | 
                  Log.PROFILE |
                  Log.CONFIG
#                  Log.EVENTS 
#                  Log.EVENTS2
                 )
Player.loadFile("remote.avg")
Player.setFramerate(60)
Tracker = Player.addTracker()
Tracker.setDebugImages(False, True)
Host = os.getenv("AVG_REMOTE_HOST")
Port = os.getenv("AVG_REMOTE_PORT")
if Host == None or Port == None:
    Log.trace(Log.WARNING, "AVG_REMOTE_HOST and/or AVG_REMOTE_PORT not set. OSC server not available.")
    OSCController = None
else:
    OSCController = controller.Controller((Host, int(Port)), verbose=True)
    Log.trace(Log.CONFIG, "OSC server opened and sending to Host "+Host+", port "+str(int(Port)))
Player.setInterval(1, onFrame)
Player.play()
