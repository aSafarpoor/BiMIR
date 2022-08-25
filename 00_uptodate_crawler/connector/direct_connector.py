import requests
from .base_connector import BaseConnector

headers = {
  'Accept': 'application/json, text/plain, */*',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}

class DirectConnector(BaseConnector):
	def __init__(self, user: str, password: str):
		self.user = user
		self.password = password
		self.session = None

	def __get_session(self) -> requests.Session:
		if self.session is None:
			self.new_session()
		return self.session

	def __logout(self):
		self.session.get('https://www.uptodate.com/logout', headers=headers)

	def new_session(self):
		if self.session is not None:
			self.__logout()
		self.session = requests.session()
		self.session.post('https://www.uptodate.com/services/app/login/json', {'userName': self.user, 'password': self.password, 'saveUserName': True, 'isSubmitting': True}, headers=headers)

	def call(self, endpoint: str, params: dict={}) -> requests.Response:
		url = f'https://www.uptodate.com/services/app{endpoint}'
		return self.__get_session().get(url, params=params, headers=headers)

