#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from xml.etree import ElementTree
import time
import urllib.request
from threading import Thread

class RssMonitor(object):
	def __init__(self, feedurl, callback):
		self.feedurl = feedurl
		self.callback = callback

		Thread(target=self.monitorloop).start()

	def getEntries(self):
		return ElementTree.parse(urllib.request.urlopen(self.feedurl)).getroot().find('channel').findall('item')

	def monitorloop(self):
		entries = self.getEntries()
		lastchange = entries[0].find('guid').text
		while True:
			entries = self.getEntries()
			for entry in entries:
				if entry.find('guid').text == lastchange:
					break
				self.callback(entry.find('title').text, entry.find('link').text)
			lastchange = entries[0].find('guid').text
			time.sleep(60)
