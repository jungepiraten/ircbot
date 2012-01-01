#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from twitter import Twitter
from threading import Thread
import time

class TwitterMonitor(object):
	def __init__(self, query, callback):
		self.query = query
		self.callback = callback

		Thread(target=self.monitorloop).start()
	
	def monitorloop(self):
		twitter = Twitter(domain="search.twitter.com")
		watermark = dict()
		while True:
			for query in self.query:
				if query in watermark:
					results = twitter.search(q=query,result_type="recent",since_id=watermark[query])
					for tweet in results["results"]:
						self.callback(	tweet["from_user"],
								"http://twitter.com/#!/" + tweet["from_user"] + "/status/" + tweet["id_str"],
								tweet["text"] )
				else:
					results = twitter.search(q=query,result_type="recent",rpp="1")
				watermark[query] = results["max_id_str"]
			time.sleep(60)
