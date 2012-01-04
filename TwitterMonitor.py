#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from twitter import Twitter
from threading import Thread
from urllib.parse import quote
import time

class TwitterMonitor(object):
	def __init__(self, query, callback):
		self.query = query
		self.callback = callback

		Thread(target=self.monitorloop).start()
	
	def monitorloop(self):
		twitter = Twitter(domain="search.twitter.com")
		results = twitter.search(q=self.query,result_type="recent",rpp="1")
		watermark = results["max_id_str"]
		while True:
			results = twitter.search(q=self.query,result_type="recent",since_id=watermark)
			for tweet in results["results"]:
				self.callback(	tweet["from_user"],
						"http://twitter.com/#!/" + quote(tweet["from_user"]) + "/status/" + tweet["id_str"],
						tweet["text"] )
			watermark = results["max_id_str"]
			time.sleep(60)
