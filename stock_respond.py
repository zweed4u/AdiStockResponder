#!/usr/bin/python3.6

import json
import tweepy
import requests
import datetime
from tweepy import Stream
from bs4 import BeautifulSoup
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

base_stock_url = 'https://www.adidas.com/on/demandware.store/Sites-adidas-US-Site/en_US/Product-Show?pid=%20'


class StdOutListener(StreamListener):
	def __init__(self, DEBUG=False):
		self.DEBUG = DEBUG
		self.tweetCount = 0

	def on_connect(self):
		print("Connection established!!\n========================")

	def on_disconnect(self, notice):
		print("Connection lost!! : ", notice)

	def on_data(self, status):
		global url, response
		status = json.loads(str(status))
		if self.DEBUG:
			print(status)
		if 'text' in status.keys():  # this is a tweet
			if status['text'].split()[0] == '@AdiStockRespond':  # make sure the tweet is a mention
				self.tweet_text = status['text']
				self.tweeters_name = status['user']['screen_name']
				self.tweeters_id = status['user']['id_str']
				self.link_to_tweet = f'https://twitter.com/{self.tweeters_name}/status/{status["id_str"]}'
				style_code = self.tweet_text.split()[1]  # tweets format must contain the style code as next 'word' after '@''
				if self.DEBUG:
					print(style_code)
				self.stock = self.fetch_style_code_stock(style_code)  # need to sanitize/check this
				print(f'{datetime.datetime.now()} :: Tweeting {self.stock} to {self.tweeters_name}')
				api.update_status(f'@{self.tweeters_name} {self.stock}', in_reply_to_status_id=status['id_str'])
				self.tweetCount += 1  # increment tweet count

	def fetch_style_code_stock(self, product_code):
		self.total_stock = 0
		session = requests.session()
		response = session.get(f'{base_stock_url}{product_code}', headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'})
		soup = BeautifulSoup(response.content, "html5lib")
		if self.DEBUG:
			print(response.content)
		stock_dict = {}
		sizes = soup.findAll('select', {'name':'pid'})[0]
		for size_option in sizes.findAll('option'):
			try:
				sizes_stock = size_option['data-maxavailable']
				qty_can_order = size_option['data-maxorderqty']
				style_size_code = size_option['value']
				size = size_option.text.strip()
				stock_dict[f'{size}'] = sizes_stock
				self.total_stock += int(float(sizes_stock))
			except:
				pass
		stock_dict['Total'] = self.total_stock
		return stock_dict

	def on_error(self, status):
		#Verbose error code
		if status == 200:
			print(str(status)+' :: OK - Success!')
		elif status == 304:
			print(str(status)+' :: Not modified')
		elif status == 400:
			print(str(status)+' :: Bad request')
		elif status == 401:
			print(str(status)+' :: Unauthorized')
		elif status == 403:
			print(str(status)+' :: Forbidden')
		elif status == 404:
			print(str(status)+' :: Not found')
		elif status == 406:
			print(str(status)+' :: Not acceptable')
		elif status == 410:
			print(str(status)+' :: Gone')
		elif status == 420:
			print(str(status)+' :: Enhance your Calm - rate limited')
		elif status == 422:
			print(str(status)+' :: Unprocessable entity')
		elif status == 429:
			print(str(status)+' :: Too many requests')
		elif status == 500:
			print(str(status)+' :: Internal server error')
		elif status == 502:
			print(str(status)+' :: Bad gateway')
		elif status == 503:
			print(str(status)+' :: Service unavailable')
		elif status == 504:
			print(str(status)+' :: Gateway timeout')
		else:
			print(str(status)+' :: Unknown')


global api
auth = tweepy.OAuthHandler('', '')
auth.secure = True
auth.set_access_token('', '')
api = tweepy.API(auth)
print(api.me().name)
stream = Stream(auth, StdOutListener())
stream.userstream()
