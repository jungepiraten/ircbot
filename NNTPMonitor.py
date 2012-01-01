#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from threading import Thread
import time
import email
from nntplib import NNTP

def decode_header(header):
	parts = email.header.decode_header(" ".join([line.strip() for line in header.split("\n")]))
	if len(parts) == 1 and parts[0][1] == None:
		return parts[0][0]
	return " ".join([part.decode(coding or "ascii") for part, coding in parts])

class NNTPMonitor(object):
	def __init__(self, nntphost, groups):
		self.nntphost = nntphost
		self.groups = groups
		self.watermark = dict()
		
		Thread(target=self.monitorloop).start()
	
	def connection(self):
		return NNTP(self.nntphost)

	def monitorloop(self):
		while True:
			conn = self.connection()
			for group, callback in self.groups:
				resp, count, first, last, name = conn.group(group)
				if name in self.watermark:
					for num in range(self.watermark[name] + 1, last + 1):
						resp, article = conn.head(num)
						lines = []
						for l in article.lines:
							lines.append(l.decode("utf-8"))
						message = email.message_from_string("\r\n".join(lines))
						callback(decode_header(message['From']), decode_header(message['Subject']))
				self.watermark[name] = last
			time.sleep(10)
