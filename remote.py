#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from libavg import avg
import OSC

def onTouch():
    Event = Player.getCurEvent()

Player = avg.Player()
Log = avg.Logger.get()
Player.setResolution(0, 640, 0, 0) 
#    Log.setFileDest("/var/log/cleuse.log")
Log.setCategories(Log.APP |
                  Log.WARNING | 
#                  Log.PROFILE |
#                  Log.PROFILE_LATEFRAMES |
#                 Log.CONFIG  
#                 Log.MEMORY  |
#                 Log.BLTS    
                  Log.EVENTS 
#                  Log.EVENTS2
                 )
Player.loadFile("remote.avg")
Player.setFramerate(60)
Tracker = Player.addTracker("/dev/video1394/0", 30, "640x480_MONO8")
Player.play()
