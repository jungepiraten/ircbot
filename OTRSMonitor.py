#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import time
import urllib.request
from threading import Thread

class OTRSMonitor(object):
	def __init__(self, otrsurl, username, password, queueid, callback):
		self.otrsurl = otrsurl
		self.username = username
		self.password = password
		self.queueid = queueid
		self.callback = callback

		Thread(target=self.monitorloop).start()
	
	def apiCall(self, params):
		params['User'] = self.username
		params['Password'] = self.password
		params['Object'] = 'iPhoneObject'
		return json.loads(urllib.request.urlopen(self.otrsurl + "json.pl?" + urllib.parse.urlencode(params)).read().decode("utf-8"))
	
	def ticketListCall(self):
		params = {}
		params['Method'] = "QueueView"
		params['Data'] = '{"QueueID":' + str(self.queueid) + '}'
		return self.apiCall(params)["Data"]
	
	def monitorloop(self):
		curArticleID = 0
		while True:
			tickets = self.ticketListCall()
			for ticket in tickets:
				if int(ticket["ArticleID"]) > curArticleID:
					if curArticleID != 0:
						self.callback(ticket["TicketNumber"], ticket["Subject"], self.otrsurl + "index.pl?Action=AgentTicketZoom;TicketID=" + str(ticket["TicketID"]) + "#" + str(ticket["ArticleID"]))
					curArticleID = int(ticket["ArticleID"])
			time.sleep(60)
