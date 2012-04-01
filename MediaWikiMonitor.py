#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import time
import urllib.request
from threading import Thread

class MediaWikiMonitor(object):
	def __init__(self, apiurl, callback):
		self.apiurl = apiurl
		self.callback = callback

		Thread(target=self.monitorloop).start()
	
	def apiCall(self, params):
		params['format'] = "json"
		return json.loads(urllib.request.urlopen(self.apiurl + "?" + urllib.parse.urlencode(params)).read().decode("utf-8"))
	
	def recentChangesCall(self, params):
		params['action'] = "query"
		params['list'] = "recentchanges"
		return self.apiCall(params)["query"]["recentchanges"]
	
	def monitorloop(self):
		lastchange = self.recentChangesCall({'rclimit':1,'rctype':'new|edit|log','rcshow':'!minor','rcprop':'timestamp|ids'}).pop()
		curTimePosition = lastchange["timestamp"]
		curRevPosition = lastchange["revid"]
		while True:
			changes = self.recentChangesCall({'rcdir':'newer','rcstart':curTimePosition,'rctype':'new|edit|log','rcshow':'!minor','rcprop':'user|timestamp|title|ids|comment'})
			for change in changes:
				if change["revid"] > curRevPosition:
					self.callback(change)
					curRevPosition = change["revid"]
					curTimePosition = change["timestamp"]
			time.sleep(60)
