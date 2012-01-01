#!/usr/bin/env python
# -*- coding: utf-8 -*-

from IRCSession import IRCSession
from TwitterMonitor import TwitterMonitor
from NNTPMonitor import NNTPMonitor
from base64 import b64encode
import time
from threading import Timer

def generateNNTPCallback(prefix, forumid):
	return lambda messageid,sender,subject:	Timer(3*60, lambda:
			irc.post(channel, prefix + subject + " (" + sender + ") - " +
					  "http://forum.junge-piraten.de/viewthread.php?boardid=" + str(forumid) + "&messageid=" + b64encode(messageid.encode("utf-8")).decode("utf-8"))
			)

def twitterCallback(sender, url, tweet):
	irc.post(channel, "[Twitter] " + sender + ": " + tweet + " - " + url)

irc = IRCSession('irc.libertirc.net', 6667, 'JuPiBot', 'jupibot', '-', None)
channel = "#jupis"
irc.post("NickServ", "identify JuPiBot ****")
time.sleep(1)
irc.join(channel)

TwitterMonitor([ channel, "JungePiraten" ], twitterCallback)

groups = []
groupfile = open("/root/nntpmls/lists.index", "r")
for line in groupfile:
	if not line.startswith("#"):
		ml, group, wiki, forumid, desc = line.strip().split(None, 4)
		groups.append([ group, generateNNTPCallback("[" + ml.upper() + "] ", forumid) ])
#groups.append( [ "pirates.youth.de.test", "[TEST] " ] )
NNTPMonitor("news.junge-piraten.de", groups)
