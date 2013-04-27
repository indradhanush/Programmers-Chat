#twisted imports
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.stdio import StandardIO

#system imports
from sys import stdout
from os.path import getsize

import pdb

class ProgrammersChatClientProtocol(LineReceiver):

	name = ''
	def __init__(self):
		ProgrammersChatClientProtocol.state = 'SETNAME'
		ProgrammersChatClientProtocol.fileName = ''
		self.fileData = ()
		self.fileSender = None
		self.state

	def connectionMade(self):
		print 'Connected to server.'
		forwarder = DataSenderProtocol(self)
		self.screen = StandardIO(forwarder)
		

	def lineReceived(self, line):
		print 'Line Received : ', line
		print 'State : ', ProgrammersChatClientProtocol.state
		if ProgrammersChatClientProtocol.state == 'CHAT':
			print 'Printing'
			self.screen.write('\n' + line + '\n' + self.name.join('<>'))
			print 'Printing finished'
		elif line.strip() == 'GETNAME':
			print('Enter Nick : ')
		elif line.strip() == 'NAMEBLOCK':
			print('Nick already in use. Try something else.')
		elif line.split()[0] == 'NAMESET':
			ProgrammersChatClientProtocol.state = 'CHAT'
			self.name = line.split()[1].strip()
		elif line.strip() == 'GET-FILE-SIZE':
			print 'Sending file size : '
			self.fileSize = getsize(ProgrammersChatClientProtocol.fileName)
			self.sendLine(str(self.fileSize))
			print 'File Size Sent'
		elif line.strip() == 'RECV-FILE':
			print 'Now sending...'
			self.sendLine(ProgrammersChatClientProtocol.fileName)
			#self.setRawMode()
			self.sendFile()
			print 'File Transfer Complete.'
			
	#def rawDataReceived(self, data):
	#	pass
	
	
	def sendFile(self):
		if not self.fileSender:
			self.fileSender =  open(ProgrammersChatClientProtocol.fileName, 'rb')
		while True:
			
			self.fileData = self.fileSender.read(256)
				
			if self.fileData:
				self.sendLine(self.fileData)
			else:
				#self.setLineMode()
				ProgrammersChatClientProtocol.state = 'CHAT'
				self.fileSender.close()
				self.fileSender = None
				self.fileData = ()
				ProgrammersChatClientProtocol.fileName = ''
				return

	def handleCOMMAND(self, command):
		commandList =  command.strip().split()
		if len(commandList) != 3: return 0
		#try:
		ProgrammersChatClientProtocol.fileName = commandList[2]
		print 'Command Received : ', commandList
		print 'File Name : ', ProgrammersChatClientProtocol.fileName
		try:
			with open(ProgrammersChatClientProtocol.fileName): 
				print 'Setting state.'
				ProgrammersChatClientProtocol.fileSize = getsize(ProgrammersChatClientProtocol.fileName)
				ProgrammersChatClientProtocol.state = 'SEND-FILE'
				print 'Setting state...'
				self.sendLine(ProgrammersChatClientProtocol.state)
				print 'Command state : ', ProgrammersChatClientProtocol.state 
				print 'Line sent...'
				#self.sendLine(self.fileName)
				#self.fileName = command.strip().split()
				#self.setRawMode()
				print 'Getting out'
				return 1
		except IOError: 
			print 'IOError'
			return -1

		
class ProgrammersChatClientProtocolFactory(ClientFactory):

	def startedConnecting(self, connector):
		print 'Connecting to Server . . .' 

	def buildProtocol(self, addr):
		protocol = ProgrammersChatClientProtocol()
		return protocol

	def clientConnectionLost(self, connector, reason):
		print 'Connection to server lost. Reason : ', reason
		
	def clientConnectionFailed(self, connector, reason):
		print 'Connection to server Failed. Reason : ', reason
		

class DataSenderProtocol(Protocol, ProgrammersChatClientProtocol):
	
	def __init__(self, dataSender):
		self.dataSender = dataSender

	def dataReceived(self, data):
		print 'Data Received : ', data
		if data == '\n':
			return
		#l = data.strip().split()
		if data[0] == '/':
			#l[0] = l[0][1:]
			#commandHandler = ProgrammersChatClientProtocol()
			flag = self.handleCOMMAND(data[1:])
			#flag = ProgrammersChatClientProtocol.handleCOMMAND(data[1:])
			if flag == 1:
				#self.state = 'SEND-FILE'
				#self.dataSender.sendLine(ProgrammersChatClientProtocol.state)
				#commandHandler.sendFile()
				print 'Successful handleCOMMAND'
				print 'State : ', ProgrammersChatClientProtocol.state
				self.dataSender.sendLine(data)
			elif flag == -1:
				print 'No such file'
			elif flag == 0:
				print 'Format send command properly : /send receiver file'
		else:
			self.dataSender.sendLine(data)


def main():
	from twisted.internet import reactor
	reactor.connectTCP('127.0.0.1', 8123, ProgrammersChatClientProtocolFactory())
	reactor.run()

if __name__ == '__main__':
	main()
