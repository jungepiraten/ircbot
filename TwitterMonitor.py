#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from threading import Thread

class IRCTwitterMonitor(object):
	def __init__(self, query, callback):
		self.query = query
		self.callback = callback

		Thread(target=self.monitorloop).start()
	
	def monitorloop(self):
		pass
