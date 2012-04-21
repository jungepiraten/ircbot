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
			results = twitter.search(q=self.query,result_type="recent",since_id=watermark,include_entities=1)
			for tweet in results["results"]:
				text = tweet["text"]
				for url in tweet["entities"]["urls"]:
					text = text.replace(url["url"], url["expanded_url"])
				self.callback(	tweet["from_user"],
						"https://twitter.com/#!/" + quote(tweet["from_user"]) + "/status/" + tweet["id_str"],
						text )
			watermark = results["max_id_str"]
			time.sleep(60)
