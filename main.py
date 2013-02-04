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
import re
from urllib.parse import urlencode, quote
import urllib.request

irc = IRCSession('82.136.38.236', 6667, 'JuPiBot', 'jupibot', 'Admin: prauscher / lutoma', None)
channels = ["#jupis","#jupis-status"]
irc.post("NickServ", "identify " + open("botauth.txt", "r").readline().strip())
time.sleep(1)
for channel in channels:
	irc.join(channel)

irc.join("#jupis-vorstand", open("vorstandircpasswd.txt", "r").readline().strip())
irc.join("#jupis-verwaltung")

def twitterCallback(sender, url, tweet):
	if not tweet.startswith("RT") and sender not in [line.strip() for line in open("twitterignore.txt", "r").readlines()]:
		for channel in channels:
			irc.post(channel, "[Twitter] " + sender + ": " + tweet + " - " + url)

TwitterMonitor("#jupis OR JungePiraten", twitterCallback)

#
# NNTP
#

def nntpCallback(prefix, forumid, messageid, sender, subject):
	if re.compile("\\[[+-][0-9]+\\]").search(subject):
		link = "-"
	else:
		link = urllib.request.urlopen("https://n.jpli.de/add.php?board="+quote(forumid)+"&message="+quote(b64encode(messageid.encode("utf-8")).decode("utf-8"))).read().decode("utf-8")
	for channel in channels:
		irc.post(channel, prefix + subject + " (" + sender + ") - " + link )

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
	if not change["user"] in ["Vorstandsbot","Opendatabot","Jupisberlin"]:
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

def generateOtrsVorstandCallback(channel, prefix):
	return lambda ticketNumber, subject, link: irc.post(channel, prefix + " [" + str(ticketNumber) + "] " + subject + " - " + link)

OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 38, generateOtrsVorstandCallback("#jupis-vorstand", ""))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 29, generateOtrsVorstandCallback("#jupis-verwaltung", "POSTSTELLE"))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 30, generateOtrsVorstandCallback("#jupis-verwaltung", "DOKUMENTE"))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 27, generateOtrsVorstandCallback("#jupis-verwaltung", "MV"))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 14, generateOtrsVorstandCallback("#jupis-verwaltung", "KONTAKT"))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 37, generateOtrsVorstandCallback("#jupis-verwaltung", "FINANZEN"))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 66, generateOtrsVorstandCallback("#jupis-verwaltung", "BUCHUNGEN"))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 69, generateOtrsVorstandCallback("#jupis-verwaltung", "ERSTATTUNGEN"))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 67, generateOtrsVorstandCallback("#jupis-verwaltung", "BEITRAEGE"))
OTRSMonitor("https://helpdesk.junge-piraten.de/otrs/", "JuPiBot", open("otrspasswd.txt", "r").readline().strip(), 68, generateOtrsVorstandCallback("#jupis-verwaltung", "RECHNUNGEN"))
