import zipfile
import datetime
import re

class Trace(object):
	Entry = namedtuple('Raw', ['datetime', 'values'])

	def __init__(self, fd):
		self.trace = []
		for line in fd:
			tokens = re.split('\s+', line.decode('utf-8').strip())
			ts = datetime.combine(
				datetime.strptime(tokens[0], '%d/%m/%Y').date(),
				datetime.strptime(tokens[1], '%H:%M').time()
				)
			entry = Entry(ts, list(map(int, tokens[2:])))
			trace.append(entry)


class Extract(object):
	def __init__(self, filename):
		self.filename = filename
		self.traces = []
		self.description = "<no extract.log found>"

		with zipfile.ZipFile(self.filename, 'r') as fd:
			for member in fd.infolist():
				if re.match('[\d_]+.txt', member.filename):
					self.traces.append(member)
				if member.filename == 'extract.log':
					self.description = zipfd.read(member).decode('iso-8859-1')

	def getTrace(member):
		with zipfile.ZipFile(self.filename, 'r') as fd:
			trace = Trace(fd.open(member, 'r'))
		return trace
