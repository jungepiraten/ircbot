#!/usr/bin/env python
# -*- coding: utf-8 -*-

from IRCSession import IRCSession
from TwitterMonitor import TwitterMonitor
from NNTPMonitor import NNTPMonitor
from MediaWikiMonitor import MediaWikiMonitor
from RssMonitor import RssMonitor
from OTRSMonitor import OTRSMonitor
from base64 import b64encode
import time
from threading import Timer
from urllib.parse import urlencode, quote

irc = IRCSession('irc.libertirc.net', 6667, 'JuPiBot', 'jupibot', 'Admin: prauscher / lutoma', None)
channels = ["#jupis","#jupis-status"]
irc.post("NickServ", "identify " + open("botauth.txt", "r").readline().strip())
time.sleep(1)
for channel in channels:
	irc.join(channel)

irc.join("#jupis-vorstand", open("vorstandircpasswd.txt", "r").readline().strip())

def twitterCallback(sender, url, tweet):
	if not tweet.startswith("RT") and sender not in [line.strip() for line in open("twitterignore.txt", "r").readlines()]:
		for channel in channels:
			irc.post(channel, "[Twitter] " + sender + ": " + tweet + " - " + url)

TwitterMonitor("#jupis OR JungePiraten", twitterCallback)

#
# NNTP
#

def nntpCallback(prefix, forumid, messageid, sender, subject):
	for channel in channels:
		irc.post(channel, prefix + subject + " (" + sender + ") - " +
# 			  "https://forum.junge-piraten.de/viewthread.php?" + urlencode({ 'boardid' : forumid, 'messageid' : b64encode(messageid.encode("utf-8")).decode("utf-8") }))
			  "https://f.jpli.de/" + quote(forumid) + "/" + quote(b64encode(messageid.encode("utf-8")).decode("utf-8")) )

def generateNNTPCallback(prefix, forumid):
	return lambda messageid,sender,subject: Timer(3*60, nntpCallback, [prefix, forumid, messageid, sender, subject] ).start()

groups = []
groupfile = open("/root/nntpmls/lists.index", "r")
for line in groupfile:
	if not line.startswith("#"):
		ml, group, wiki, forumid, desc = line.strip().split(None, 4)
		groups.append([ group, generateNNTPCallback("[" + ml.upper() + "] ", forumid) ])

NNTPMonitor("news.junge-piraten.de", groups)

#
# Wiki LastChanges
#

def mediawikiCallback(change):
	for channel in channels:
		irc.post(channel, "[Wiki] " + change["title"] + " (" + change["user"] + ": " + change["comment"] + ") - " +
					"https://wiki.junge-piraten.de/w/index.php?" + urlencode({ 'diff' : change["revid"], 'oldid' : change["old_revid"] }))

MediaWikiMonitor("https://wiki.junge-piraten.de/w/api.php", mediawikiCallback)

#
# Homepage (Artikel & Kommentare)
#

def homepageArticleCallback(title,link):
	for channel in channels:
		irc.post(channel, "[HOMEPAGE] " + title + " - " + link)

RssMonitor("http://www.junge-piraten.de/feed/", homepageArticleCallback)

def homepageCommentCallback(title,link):
	for channel in channels:
		irc.post(channel, "[HOMEPAGE] " + title + " - " + link)

RssMonitor("http://www.junge-piraten.de/comments/feed/", homepageCommentCallback)

#
# OTRS (Vorstandsqueue)
#

def otrsVorstandCallback(ticketNumber, subject, link):
	irc.post("#jupis-vorstand", "[" + str(ticketNumber) + "] " + subject + " - " + link)

OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 38, otrsVorstandCallback)
