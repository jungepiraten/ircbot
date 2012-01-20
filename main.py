#!/usr/bin/env python
# -*- coding: utf-8 -*-

from IRCSession import IRCSession
from TwitterMonitor import TwitterMonitor
from NNTPMonitor import NNTPMonitor
from MediaWikiMonitor import MediaWikiMonitor
from base64 import b64encode
import time
from threading import Timer
from urllib.parse import urlencode

def generateNNTPCallback(prefix, forumid):
	return lambda messageid,sender,subject:	Timer(3*60, lambda:
			irc.post(channel, prefix + subject + " (" + sender + ") - " +
					  "http://forum.junge-piraten.de/viewthread.php?" + urlencode({ 'boardid' : forumid, 'messageid' : b64encode(messageid.encode("utf-8")).decode("utf-8") }))
			).start()

twitterIgnoreList = [line.strip() for line in open("twitterignore.txt", "r").readlines()]

def twitterCallback(sender, url, tweet):
	if sender not in twitterIgnoreList:
		irc.post(channel, "[Twitter] " + sender + ": " + tweet + " - " + url)

def mediawikiCallback(change):
	irc.post(channel, "[Wiki] " + change["title"] + " (" + change["user"] + ") - " +
				"http://wiki.junge-piraten.de/w/index.php?" + urlencode({ 'diff' : change["revid"], 'oldid' : change["old_revid"] }))

irc = IRCSession('irc.libertirc.net', 6667, 'JuPiBot', 'jupibot', 'Admin: prauscher / lutoma', None)
channel = "#jupis"
irc.post("NickServ", "identify " + open("botauth.txt", "r").readline().strip())
time.sleep(1)
irc.join(channel)

TwitterMonitor("#jupis OR JungePiraten", twitterCallback)

groups = []
groupfile = open("/root/nntpmls/lists.index", "r")
for line in groupfile:
	if not line.startswith("#"):
		ml, group, wiki, forumid, desc = line.strip().split(None, 4)
		groups.append([ group, generateNNTPCallback("[" + ml.upper() + "] ", forumid) ])
#groups.append( [ "pirates.youth.de.test", "[TEST] " ] )
NNTPMonitor("news.junge-piraten.de", groups)

MediaWikiMonitor("http://wiki.junge-piraten.de/w/api.php", mediawikiCallback)
