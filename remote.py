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
    if Event.type == avg.MOUSEBUTTONDOWN:
        Type = "down"
    elif Event.type == avg.MOUSEBUTTONUP:
        Type = "up"
    elif Event.type == avg.MOUSEMOTION:
        Type = "motion"
    else:
        print Event.type
    OSCController.sendMsg('/touch/'+Type, int(Event.cursorid), float(Event.x), float(Event.y))

Player = avg.Player()
Log = avg.Logger.get()
Player.setResolution(0, 640, 0, 0) 
Log.setCategories(Log.APP |
                  Log.WARNING | 
#                  Log.PROFILE |
                  Log.CONFIG | 
                  Log.EVENTS 
#                  Log.EVENTS2
                 )
Player.loadFile("remote.avg")
Player.setFramerate(60)
Tracker = Player.addTracker("/dev/video1394/0", 30, "640x480_MONO8")
OSCController = controller.Controller((HOST, PORT), verbose=True)
Player.play()
