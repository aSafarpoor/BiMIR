from connector import *
from uptodate_crawler import UptodateCrawler
import pymongo

MONGO_INFO = 'mongodb://root:example@localhost:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&ssl=false'

IRAN_PAPER_LOGIN = ['mohalisad', 'p:159357']
UPTODATE_LOGIN = ["mod723bh2@icloud.com", "7Pc1V9KPUBaz"]

if __name__ == '__main__':
	db_connection = pymongo.MongoClient(MONGO_INFO)
	connector = DirectConnector(*UPTODATE_LOGIN)
	crawler = UptodateCrawler(connector, db_connection["uptodate"])
	crawler.start_crawl()
