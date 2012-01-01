#!/usr/bin/env python
# -*- coding: utf-8 -*-

from IRCSession import IRCSession
from TwitterMonitor import TwitterMonitor
from NNTPMonitor import NNTPMonitor

def generateNNTPCallback(prefix):
	return lambda sender,subject: irc.post(channel, prefix + subject + " (" + sender + ")")

def twitterCallback(sender, url, tweet):
	irc.post(channel, "[Twitter] " + sender + ": " + tweet + " (" + url + ")")

irc = IRCSession('schumann.de.libertirc.net', 6667, 'JuPiBot', 'jupibot', '-', None)
channel = "#test"
irc.join(channel)

TwitterMonitor([ "#jupis", "JungePiraten" ], twitterCallback)

groups = []
groupfile = open("/root/nntpmls/lists.index", "r")
for line in groupfile:
	if not line.startswith("#"):
		ml, group, wiki, id, desc = line.strip().split(None, 4)
		groups.append([ group, generateNNTPCallback("[" + ml.upper() + "] ") ])
#groups.append( [ "pirates.youth.de.test", "[TEST] " ] )
NNTPMonitor("news.junge-piraten.de", groups)
