import abc
import requests


class BaseConnector(abc.ABC):
	@abc.abstractmethod
	def new_session(self):
		pass

	@abc.abstractmethod
	def call(self, endpoint: str, params: dict={}) -> requests.Response:
		pass

	def call_json(self, endpoint: str, params: dict={}):
		response = self.call(endpoint + '/json', params)
		try:
			return response.json(), True
		except Exception as ex:
			return response.text, False