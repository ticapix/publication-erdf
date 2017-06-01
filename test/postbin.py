import json
import requests

class PostBinMailgun(object):
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
			return json.loads(messages[0]['params'])
		return None


class PostBinAppsattic(object):
	def __init__(self):
		self.api_url = "http://postb.in/api/bin"

	def create(self):
		response = requests.post(self.api_url)
		self.bin_id = response.json()['binId']
		self.url = "http://postb.in/{id}".format(id=self.bin_id)
		return self

	def delete(self):
		return requests.delete("{api_url}/{id}".format(api_url=self.api_url, id=self.bin_id))

	def retrieveOne(self):
		response = requests.get("{api_url}/{id}/req/shift".format(api_url=self.api_url, id=self.bin_id))
		if response.status_code != 200:
			return None
		return response.json()['body']

class PostBin(PostBinAppsattic):
	pass
