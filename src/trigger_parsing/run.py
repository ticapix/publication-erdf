import os
import json
import urlparse
import zipfile
from tempfile import SpooledTemporaryFile
import re
from collections import namedtuple
from datetime import datetime, time

os.sys.path.append(os.path.realpath(os.environ['PACKAGES_DIR']))

# if 'TEST_ID' in os.environ:
# 	print('execution in dev environment')
# 	envfile = os.path.join(os.path.dirname(__file__), 'test', 'dump-{}-env.json'.format(os.environ['TEST_ID']))
# 	print('loading environment from {}'.format(envfile))
# 	os.environ.update(json.load(open(envfile, 'r')))
# 	os.environ['REQ'] = os.path.join(os.path.dirname(__file__), 'test', 'dump-{}-body.dat'.format(os.environ['TEST_ID']))
# 	# to hide SNIMissingWarning and InsecurePlatformWarning warnings
# 	import requests.packages.urllib3
# 	requests.packages.urllib3.disable_warnings()
# 	# to activate cache during dev
# 	import requests_cache
# 	requests_cache.install_cache('demo_cache')
# else:
	# os.sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), 'venv', 'Lib', 'site-packages'))

import requests
import pygal
from jinja2 import Template

def getEmailOptions(message):
	recipient = message['recipient']
	print(recipient)
	ans = re.match('^[^\+]+(\+(?P<args>.*))?@.*$', recipient)
	args = ans.group('args')
	args = dict([arg.split('=', 1) for arg in args.split('|')]) if args else {}
	return args

def getEmailAttachment(message):
	print('receiving email from {} ({})'.format(message['from'], message['sender']))
	print('subject: {}'.format(message['subject']))
	print('email body: {}'.format(repr(message['body-plain'])))
	if 'attachments' not in message:
		return
	for attachment in json.loads(message['attachments']):
		print('attachment {name} of type {content-type}'.format(**attachment))
		yield attachment

def parse(message):
	results = {'options': getEmailOptions(message),
		'attachments': {},
		'body-plain': repr(message['body-plain'][0])
	}

print(__name__)

if __name__ == '__main__':
	# read the queue message and write to stdout
	content_type = os.environ['REQ_HEADERS_CONTENT-TYPE']
	if content_type != 'application/x-www-form-urlencoded':
		print('unknown content-type {}'.format(content_type))
		os.sys.exit(1)
	message = dict(urlparse.parse_qsl(open(os.environ['REQ']).read()))
	parse(message)
	os.sys.exit(0)

	session = requests.Session()
	session.auth = ('api', os.environ['MG_API_KEY'])




def parseTrace(fd):
	Entry = namedtuple('Raw', ['datetime', 'nums'])
	trace = []
	for line in fd:
		tokens = re.split('\s+', line.decode('utf-8').strip())
		ts = datetime.combine(
			datetime.strptime(tokens[0], '%d/%m/%Y').date(),
			datetime.strptime(tokens[1], '%H:%M').time()
			)
		entry = Entry(ts, list(map(int, tokens[2:])))
		trace.append(entry)
	return trace

def extractTraces(zip_path):
	results = {'traces': {}}
	with zipfile.ZipFile(zip_path, 'r') as zipfd:
		for info in zipfd.infolist():
			if re.match('[\d_]+.txt', info.filename):
				results['traces'][info.filename] = parseTrace(zipfd.open(info, 'r'))
			if info.filename == 'extract.log':
				results['description'] = zipfd.read(info).decode('iso-8859-1')
	return results

# data = urlparse.parse_qs(open(os.environ['REQ']).read())
# results = {'options': getEmailOptions(data),
# 	'attachments': {},
# 	'body-plain': repr(data['body-plain'][0])
# }
# for attachment in getEmailAttachment(data):
# 	if attachment['content-type'] != 'application/zip':
# 		continue
# 	print('processing attachment at url {url}'.format(**attachment))
# 	response = session.get(attachment['url'])
# 	# load file into memory
# 	with SpooledTemporaryFile() as fd:
# 		for chunk in response.iter_content(chunk_size=128):
# 			fd.write(chunk)
# 		results['attachments'][attachment['name']] = extractTraces(fd)

def calculateTotalkW(trace, options):
	capfct = lambda x: x
	if 'cap' in options:
		capfct = lambda x: min(x, int(options['cap']))
	total = 0
	for entry in trace:
		total += sum(map(capfct, entry.nums))
	print(int(total/6.), 'kW')

def formatPerHour(trace):
	Entry = namedtuple('PerHour', ['datetime', 'num'])
	return map(lambda x: Entry(x.datetime, sum(x.nums)/6.), trace)

def formatPerHourCapped(trace, options):
	Entry = namedtuple('PerHour', ['datetime', 'num'])
	threshold = int(options['cap'])
	threshold = 400
	return map(lambda x: Entry(x.datetime, sum(map(lambda x: min(x, threshold), x.nums))/6.), trace)

def formatPerDay(trace):
	def getDateBin(dt):
		return datetime.combine(dt.date(), time(23, 59))
		# return datetime.combine(dt.date(), time(11, 59) if dt.time() < time(11, 59) else time(23, 59))
	res = []
	Entry = namedtuple('PerDay', ['date', 'num'])
	day = getDateBin(trace[0].datetime)
	day_vals = []
	for entry in trace:
		if entry.datetime < day:
			day_vals.append(entry.num)
		else:
			res.append(Entry(day, sum(day_vals) / len(day_vals)))
			day = getDateBin(entry.datetime)
			day_vals = [entry.num]
	return res

# for name, attachment in results['attachments'].items():
# 	print('processing attachment {}'.format(name))
# 	for name, traces in attachment['traces'].items():
# 		attachment['traces'][name] = {
# 			'raw': traces,
# 			'perhour': formatPerHour(traces)
# 			}
# 		attachment['traces'][name]['perday'] = formatPerDay(attachment['traces'][name]['perhour'])
# 		attachment['traces'][name]['total_kW'] = sum(map(lambda x: x.num, attachment['traces'][name]['perhour']))
# 		print('trace {}: total of {} kw'.format(name, attachment['traces'][name]['total_kW']))
# 		date_chart = pygal.Line(
# 			x_label_rotation=20,
# 			height=200,
# 			width=600,
# 			legend_at_bottom=True
# 			)
# 		date_chart.x_labels = map(lambda d: d.strftime('%Y-%m-%d') if d.day % 2 else '', map(lambda x: x.date, attachment['traces'][name]['perday']))
# 		# date_chart.x_value_formatter = lambda x: '%s%%' % x
# 		date_chart.add("kW", map(lambda x: x.num, attachment['traces'][name]['perday']),
# 			)
# 		if 'cap' in results['options']:
# 			attachment['traces'][name]['perhour_capped'] = formatPerHourCapped(traces, results['options'])
# 			attachment['traces'][name]['perday_capped'] = formatPerDay(attachment['traces'][name]['perhour_capped'])
# 			attachment['traces'][name]['total_capped_kW'] = sum(map(lambda x: x.num, attachment['traces'][name]['perhour_capped']))
# 			print('trace {}: total of {} kW with cap at {} kW'.format(name, attachment['traces'][name]['total_capped_kW'], results['options']['cap']))
# 			date_chart.add("kW (capped)", map(lambda x: x.num, attachment['traces'][name]['perday_capped']),
# 				)
# 		attachment['traces'][name]['graph'] = date_chart.render(is_unicode=True)
# template_file = os.path.join(os.path.dirname(__file__), 'email_tpl.html')
# template = Template(open(template_file, 'r').read())
# html = template.render(results=results)

# res = session.post('https://api.mailgun.net/v3/{domain}/messages'.format(domain='mg.turbinealternateur.fr'),
# 	data={
# 		'from': 'bnpr-pub@mg.turbinealternateur.fr', #data['recipient'][0],
# 		'to': data['sender'][0],
# 		'subject': data['subject'][0],
# 		'html': html
# 	}
# 	)
# print(res.status_code, res.text)


 # strftime, the equivalent argument string is "%Y-%m-%d %H:%M:%S" 