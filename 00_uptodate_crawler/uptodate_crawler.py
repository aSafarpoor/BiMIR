import time
import connector.base_connector as bc
import pymongo.database


class UptodateCrawler:
	def __init__(self, connector: bc.BaseConnector, mongo_db: pymongo.database.Database):
		self.topics = mongo_db["topics"]
		self.errors = mongo_db["errors"]
		self.skips = mongo_db["skips"]
		
		self.level = 0
		self.counter = 0
		self.connector = connector
		self.stack = []

		self.last_period = 0

		self.seen = {}
		seen_endpoints = self.topics.aggregate([{'$project': {'endpoint': '$endpoint'}}])
		for item in seen_endpoints:
			self.seen[item['endpoint']] = 1

	def log_info(self, name):
		self.counter += 1
		print('{0:06d}'.format(self.counter) + '│' * (self.level - 1) + f'├{name}')

	def log_error(self, data, kind):
		print(f"_____ERROR{kind}_____")
		print(data)
		exit()

	def periodic_check(self):
		if self.counter - self.last_period > 15:
			self.last_period = self.counter
			self.connector.new_session()
			self.__dummy_search()

	def parse_data(self, data, endpoint):
		time.sleep(1)
		self.periodic_check()
		self.level += 1
		if 'type' in data:
			self.log_info(data["name"])

			self.stack.append(data["name"])

			if data['type'] == 'TOP_LEVEL_TOC':
				self.parse_items(data)
			elif data['type'] == 'SPECIALTY':
				if data['name'] not in ["Calculators", "Lab Interpretation", "Pathways"]:
					self.parse_items(data)
			elif data['type'] == 'SECTION':
				self.parse_sections(data)
			elif data['type'] == 'CONTRIBUTOR':
				pass
			else:
				self.log_error(data['type'], 1)

			self.stack.pop()

		elif 'topicInfo' in data:
			self.parse_topic(data, endpoint)
		else:
			self.log_error(data, 2)

		self.level -= 1

	def parse_sections(self, data):
		if 'sections' in data:
			for section in data['sections']:
				self.parse_sections(section)
		elif 'items' in data:
			self.parse_items(data)
		elif 'subSections' in data:
			for section in data['subSections']:
				self.parse_sections(section)
		else:
			self.log_error(data, 4)

	def parse_items(self, data):
		for item in data['items']:
			endpoint = item['url']
			if item['type'] == 'TOPIC':
				endpoint = '/contents/topic/' + endpoint.split('/')[-1]
			self.__call_and_parse(endpoint)

	def parse_topic(self, data, endpoint):
		self.log_info(data["topicInfo"]["title"])
		data["endpoint"] = endpoint
		data["topics_stack"] = self.stack
		self.topics.insert_one(data)

	def __dummy_search(self):
		params = {
			'autoComplete': False,
			'autoCompleteTerm': None,
			'index': None,
			'language': 'en',
			'max': 40,
			'search': 'drug',
			'searchControl': 'TOP_PULLDOWN',
			'searchOffset': 1,
			'searchType': 'PLAIN_TEXT',
			'source': 'USER_INPUT',
			'sp': 0
		}
		res = self.connector.call_json('/contents/search/2', params)

	def __call_and_parse(self, endpoint):
		if endpoint not in self.seen:
			while True:
				response, ok = self.connector.call_json(endpoint)
				if ok:
					data = response['data']
					error_check = self.__check_errors(data)
					if error_check == 0:
						break
					elif error_check == 2:
						self.log_info('_____SKIP_____')
						self.periodic_check()	
						self.skips.insert_one({'endpoint': endpoint, 'data': response, 'topics_stack': self.stack})
						return
					elif error_check == 3:
						self.log_error(endpoint, 4)
				else:
					self.errors.insert_one({'endpoint': endpoint, 'data': response, 'topics_stack': self.stack})
					return
			self.seen[endpoint] = 1
			self.parse_data(data, endpoint)
		else:
			self.log_info('_____SEEN_____')

	def __check_errors(self, data):
		check = 1 if 'errors' in data else 0
		if check == 1:
			for error in data['errors']:
				if error['utdStatus'] == 'REQUESTS_PER_SEARCH_LIMIT':
					self.__dummy_search()
				elif error['utdStatus'] == 'REQUESTS_PER_SESSION_LIMIT':
					self.connector.new_session()
					time.sleep(10)
				elif error['utdStatus'] in ['FORBIDDEN', 'RESOURCE_NOT_FOUND']:
					check = 2
				else:
					self.log_error(error['utdStatus'], 3)

		return check

	def start_crawl(self):
		self.__call_and_parse('/contents/table-of-contents')
