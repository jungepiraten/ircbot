#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from threading import Thread
from twython import Twython
import time

class TwitterMonitor(object):
	def __init__(self, query, callback):
		self.query = query
		self.callback = callback

		Thread(target=self.monitorloop).start()
	
	def monitorloop(self):
		twitter = Twython()
		watermark = dict()
		while True:
			for query in self.query:
				if query in watermark:
					results = twitter.searchTwitter(q=query,result_type="recent",since_id=watermark[query])["results"]
				else:
					results = twitter.searchTwitter(q=query,result_type="recent")["results"]
				for tweet in results:
					self.callback(tweet["from_user"], "http://twitter.com/#!/" + tweet["from_user"] + "/status/" + tweet["id_str"], tweet["text"])
					watermark[query] = tweet["id_str"]
			time.sleep(60)
