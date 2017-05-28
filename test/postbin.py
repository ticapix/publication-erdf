import requests

class PostBin(object):
	def __init__(self):
		self.ids = []

	def create(self):
		self.url = requests.get("http://bin.mailgun.net/api/new").json()['url']
		return self

	def delete(self):
		return requests.delete(self.url)

	def retrieveOne(self):
		messages = requests.get(self.url).json()
		messages = filter(lambda m: m['id'] not in self.ids, messages)
		if len(messages):
			self.ids.append(messages[0]['id'])
			return messages[0]
		return None
