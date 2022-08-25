import requests
import re
from .base_connector import BaseConnector


class IranpaperUptodateConnector(BaseConnector):
	def __init__(self, user: str, password: str):
		self.user = user
		self.password = password
		self.token = None

	def __generate_token(self):
		login_session = requests.Session()
		login_session.post('https://iranpaper.ir/login/includes/posthandler.php', {'username': self.user, 'password': self.password, 'login': 'Login'})
		response = login_session.get('https://iranpaper.ir/')
		return re.findall(r'uptodate.com.(\w+)', response.text)[0]

	def __get_token(self):
		if self.token is None:
			self.new_session()
		return self.token

	def new_session(self):
		self.token = self.__generate_token()

	def call(self, endpoint: str, params: dict={}):
		url = f'http://eznl-https-www.uptodate.com.{self.__get_token()}.di-iranpaper.ir/services/app{endpoint}'
		# print(url)
		return requests.get(url, params=params)

	def call_json(self, endpoint: str, params: dict={}):
		response = self.call(endpoint + '/json', params)
		try:
			return response.json(), True
		except Exception as ex:
			return response.text, False