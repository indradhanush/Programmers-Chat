from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


class ProgrammersChatProtocol(LineReceiver):
	
	def __init__(self, users):
		self.users = users
		self.name = None
		self.state = 'GETNAME'
		self.fileReceiver = None
		self.fileData = ()

	def connectionMade(self):
		self.peerIP = self.transport.getPeer()
		print self.peerIP, 'has joined.'
		self.sendLine('GETNAME')
		
	def connectionLost(self, reason):
		print 'Connection lost.'
		print self.name
		if self.users.has_key(self.name):
			print '%s  has left : %s' % (self.name.strip(), reason)
			del self.users[self.name]

	def lineReceived(self, line):
		print 'Line Received : ', line
		print 'State : ', self.state
		if line == '\n':
			return
		elif self.state == 'GETNAME':
			self.handleGETNAME(line)
		
		elif self.state == 'CHAT':
			line = line.strip()
			if line.split()[0][0] == '/':
				print 'handle comand called`'
				self.handleCOMMAND(line[1:])	
			else:
				line = self.name.strip().join('<>') + ' ' + line
				self.handleCHAT(line)
		#elif line.strip() == 'SEND-FILE':
		#	print 'Received : ', line
		#	self.state = 'GET-FILE-SIZE'
		#	self.sendLine(self.state)
		
		elif self.state == 'GET-FILE-SIZE':
			self.fileSize = int(line.strip())
			print 'File Size : ', self.fileSize
			self.state = 'RECV-FILE'
			self.sendLine(self.state)
		elif self.state == 'RECV-FILE':
			self.fileData = self.fileName
			print 'Receiving file : %s' % (self.fileName)
			self.setRawMode()
		
		
		
	def rawDataReceived(self, data):
		print 'Receiving file chunk %d KB' % (len(data))
		self.filePath = '/home/dhanush/programmers_chat/downloads/' + self.fileName
		if not self.fileReceiver:
			self.fileReceiver = open(self.filePath, 'wb')

		#if data.endswith(\r\n):
		#	self.fileReceiver.write(data)
		#	self.fileSize -= len(data)
		#	print 'File Data :>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', data
		if data.endswith('\r\n') :
			self.fileReceiver.write(data[:-2])
			#self.setLineMode()
			
			#print 'File Transfer Complete.'
			self.fileReceiver.close()
			self.fileReceiver = None
			self.fileData = ()
			self.state = 'CHAT'
			self.setLineMode()
			print 'File Transfer complete'
			return
		else:
			self.fileReceiver.write(data)
			
	def handleGETNAME(self, name):
		if self.users.has_key(name):
			print 'Name in use'
			self.sendLine('NAMEBLOCK')
			return
		
		self.name = name
		self.users[name] = self
		self.state = 'CHAT'
		nickConfirm = 'NAMESET' + ' ' + self.name.strip()
		self.sendLine(nickConfirm)
		self.sendLine("Welcome %s (%s) to  Programmer's Chat, Beta...\n" % (self.name.split(), self.peerIP))
		print '%s is using %s as UserName.' % (self.peerIP, self.name.split())

	def handleCHAT(self, message):
		print message
		for name, protocol in self.users.iteritems():
			if protocol != self:
				protocol.sendLine(message)

	def handleCOMMAND(self, command):
		### TO DO : log the command
		print 'Command : ', command
		if command == 'online':
			onlineList = ''
			for name, protocol in self.users.iteritems():
				onlineList += ' ' + str(name)
			
			for name, protocol in self.users.iteritems():
				if protocol == self:
					self.sendLine(onlineList)
					return
		
		if command.split()[0] == 'send':
			print '%s wants to send a file' % (self.name.strip())
			self.state = 'GET-FILE-SIZE'
			self.fileName = command.split()[2]
			print 'State : ', self.state
			self.sendLine(self.state)
			print 'FileName : %s' % (self.fileName)

class ProgrammersChatFactory(ServerFactory):

	def __init__(self):
		self.users = {} 

	def buildProtocol(self, addr):
		return ProgrammersChatProtocol(self.users)

reactor.listenTCP(8123,  ProgrammersChatFactory())
reactor.run()
