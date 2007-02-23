#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from libavg import avg
import OSC
import socket

HOST='localhost'
PORT=2222

global OSCSocket

def onTouch():
    Event = Player.getCurEvent()
    if Event.type == avg.MOUSEBUTTONDOWN:
        Type = "down"
    elif Event.type == avg.MOUSEBUTTONUP:
        Type = "up"
    elif Event.type == avg.MOUSEMOTION:
        Type = "motion"
    else:
        print Event.type
    msg = OSC.Message('/touch/'+Type, Event.cursorid, Event.x, Event.y)
    print msg.get_packet()
    OSCSocket.sendto(msg.get_packet(), (HOST, PORT))

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
OSCSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
Player.play()
