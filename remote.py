#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from libavg import avg
import OSC
import controller
import socket

HOST='10.0.0.142'
#HOST='localhost'
PORT=9000

def onTouch():
    global OSCController
    global HOST
    global PORT
    Event = Player.getCurEvent()
    if Event.type == avg.CURSORDOWN:
        Type = "down"
    elif Event.type == avg.CURSORUP:
        Type = "up"
    elif Event.type == avg.CURSORMOTION:
        Type = "motion"
    else:
        print Event.type
    OSCController.sendMsg('/touch/'+Type, int(Event.cursorid), 
            float(Event.x), float(Event.y))

def onKeyUp():
    Event = Player.getCurEvent()
    if Event.keystring == "s":
        Tracker.saveConfig()
        print ("Tracker configuration saved.")

def flipBitmap(Node):
    for y in range(Node.getNumVerticesY()):
        for x in range(Node.getNumVerticesX()):
            pos = Node.getOrigVertexCoord(x,y)
            pos.y = 1-pos.y
            Node.setWarpedVertexCoord(x,y,pos)

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
#Player.setResolution(0, 640, 0, 0) 
Player.setResolution(1, 0, 0, 0) 
Log.setCategories(Log.APP |
                  Log.WARNING | 
#                  Log.PROFILE |
                  Log.CONFIG
#                  Log.EVENTS 
#                  Log.EVENTS2
                 )
Player.loadFile("remote.avg")
Player.setFramerate(60)
Tracker = Player.addTracker("/dev/video1394/0", 60, "640x480_MONO8")
Tracker.setDebugImages(False, True)
OSCController = controller.Controller((HOST, PORT), verbose=True)
Player.setInterval(1, onFrame)
Player.play()
