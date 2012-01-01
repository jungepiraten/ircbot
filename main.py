#!/usr/bin/env python
# -*- coding: utf-8 -*-

from IRCSession import IRCSession
from TwitterMonitor import TwitterMonitor
from NNTPMonitor import NNTPMonitor
from base64 import b64encode

def generateNNTPCallback(prefix, forumid):
	return lambda messageid,sender,subject: irc.post(channel, prefix + subject + " (" + sender + ") - "
					+ "http://forum.junge-piraten.de/viewthread.php?boardid=" + str(forumid) + "&messageid=" + b64encode(messageid.encode("utf-8")))

def twitterCallback(sender, url, tweet):
	irc.post(channel, "[Twitter] " + sender + ": " + tweet + " - " + url)

irc = IRCSession('irc.libertirc.net', 6667, 'JuPiBot', 'jupibot', '-', None)
channel = "#jupis"
irc.join(channel)
irc.post("NickServ", "identify JuPiBot BEgkVPMQT9y9dehe")

TwitterMonitor([ channel, "JungePiraten" ], twitterCallback)

groups = []
groupfile = open("/root/nntpmls/lists.index", "r")
for line in groupfile:
	if not line.startswith("#"):
		ml, group, wiki, forumid, desc = line.strip().split(None, 4)
		groups.append([ group, generateNNTPCallback("[" + ml.upper() + "] ", forumid) ])
#groups.append( [ "pirates.youth.de.test", "[TEST] " ] )
NNTPMonitor("news.junge-piraten.de", groups)
