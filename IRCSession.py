#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread, Lock
import socket
import random
import time
import sys

class IRCSession(object):
	def __init__(self, server, port, nickname, username, realname, password):
		self.s = socket.socket()
		self.s.connect((server,port))
		self.rbuf = self.s.makefile("rb")
		
		self.omegle = {}
		self.player = {}
		self.nickname = nickname

		self.privmsgHooks = dict()
		
		if password:
			self.send("PASS {0}".format(password))
		self.send("NICK {0}".format(nickname))
		self.send("USER {0} 127.0.0.1 {1} :{2}".format(username, server, realname))
		Thread(target=self.readloop).start()
		# Wait until MOTD etc gets done
		time.sleep(3)

	# our debug-hook - in most cases do nothing
	def debug(self, msg):
		print(msg)
		pass
	
	def send(self, data):
		self.debug(' > ' + data)
		self.s.send(data.encode('utf-8') + b'\n')
	
	def readloop(self):
		while True:
			try:
				line = self.rbuf.readline().strip().decode('utf-8')
				self.debug(' < ' + line)
				self.parseLine(line)
			except UnicodeDecodeError:
				pass
	
	def join(self, chan):
		self.send('JOIN {0}'.format(chan))

	def leave(self, chan, reason):
		self.send('PART {0} :{1}'.format(chan, reason))
	
	def post(self, chan, msg):
		for line in msg.split('\n'):
			self.send('PRIVMSG {0} :{1}'.format(chan, line.rstrip()))

	def registerCommand(self, prefix, function):
		self.privmsgHooks[prefix] = function
	
	def parseLine(self, line):
		if line == '' or line == None:
			return
		# irc-syntax. ":nick!user@host restofline"
		if line.startswith(':'):
			source = line.split(' ', 2)[0].lstrip(':').split('!', 2)[0].lower()
			line = ' '.join(line.split(' ', 2)[1:])

		# nick is in use
		if line.startswith('433'):
			self.nickname = self.nickname + "_"
			self.send('NICK ' + self.nickname)

		# handle commands via PRIVMSG
		elif line.upper().startswith('PRIVMSG'):
			# irc-syntax. "PRIVMSG <target> <message>"

			(cmd, chan) = line.split(' ')[0:2]
			if not chan.startswith('#'):
				chan = source
			body = ' '.join(line.split(' ')[2:])
			# irc-clients have to send a prefixed message to be rfc-compatible
			if body.startswith(':'): body = body[1:]
			
			for command in self.privmsgHooks.keys():
				if body.lower().startswith(command.lower()):
					self.privmsgHooks[command](IRCContext(self, chan, source), command, body[len(command):])

		# only needed if we want to auto-join every channel we get invited to
		#elif line.upper().startswith('INVITE'):
		#	(cmd, nick) = line.split(' ')[0:2]
		#	chan = line.split(' ')[2]
		#	if chan.startswith(':'): chan = chan[1:]
		#	self.join(chan)

		# reply PINGs (else connection will be closed by server)
		elif line.upper().startswith('PING'):
			self.send('PONG ' + line[5:])

class IRCContext(object):
	def __init__(self, irc, channel, sender):
		self.irc = irc
		self.channel = channel
		self.sender = sender

	def reply(self, message):
		self.irc.post(self.channel, self.sender + ": " + message)
