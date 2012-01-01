#!/usr/bin/env python
# -*- coding: utf-8 -*-

from IRCSession import IRCSession
from IRCTwitterMonitor import IRCTwitterMonitor
from NNTPMonitor import NNTPMonitor

irc = IRCSession('irc.libertirc.net', 6667, 'JuPiBot', 'jupibot', '-', None)
channel = "#test"

def generateNNTPCallback(prefix):
	return lambda sender,subject: irc.post(channel, prefix + subject + " (" + sender + ")")

def twitterCallback(sender, url, tweet):
	irc.post(channel, "[Twitter] " + sender + ": " + tweet + " (" + url + ")")

TwitterMonitor([ "#jupis", "JungePiraten" ], twitterCallback)
NNTPMonitor("news.junge-piraten.de",
	[
	[ "pirates.youth.de.test", generateNNTPCallback("[Test] ") ]
	] )

irc.join(channel)
