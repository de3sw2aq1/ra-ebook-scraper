#!/usr/bin/env python

import requests
from lxml import html
from lxml.etree import Comment
import logging
import json
from sys import exit
from urlparse import urljoin

FIRST_URL = 'http://qntm.org/city'
JSON_PATH = 'scrape.json'

def get(url):
	r = requests.get(url)
	return html.fromstring(r.text)

def getNextUrl(content, url):
	next_h4 = content.xpath('h4')[-1]
	if next_h4.text == 'Next: ':
		content.remove(next_h4)
		return urljoin(url, next_h4[0].get('href'))
	elif next_h4.text == 'To be continued':
		return None
	elif len(next_h4) == 0:
		return None  # No child elements, including <a>, which should mean last page
	else:
		logger.warn('Unkown last h4')
		# IPython.embed()
		exit('Giving up')

logging.basicConfig()
logger = logging.getLogger("scraper")
logger.setLevel(logging.DEBUG)

url = FIRST_URL
i = 1

try:
	with open(JSON_PATH, 'r') as outfile:
		pages = json.load(outfile)
except IOError, e:
	pages = []

if pages:
	url = pages[-1]['url']
	i = pages[-1]['id'] + 1

	logger.info('Requesting: ' + url)
	src = get(url)
	logger.info('Looking for new pages')
	url = getNextUrl(src.xpath("//div[@id='content']")[0], url)
	if not url:
		exit("No new pages")

print "Starting"

while url:
	logger.info('Requesting: ' + url)
	src = get(url)
	content = src.xpath("//div[@id='content']")[0]
	title = src.xpath("//h2")[0]

	# Convert contents to actual tag
	for c in content.iter(Comment):
		logger.warn('Detected commment' )
		logger.debug('Comment text:' + c.text)

	url = getNextUrl(content, url)

	try:
		prev_h4 = content.xpath('h4')[0]
		if prev_h4[0].tag == 'a' and prev_h4[0].text == 'Previously':
			content.remove(prev_h4)
	except IndexError, e:
		pass

	page = {'id': i, 'url': url, 'title': title.text, 'text': html.tostring(content)}

	logger.info('Processed: ' + title.text)
	pages.append(page)

	if i % 100 == 0:
		logger.info('Dumping json')
		with open(JSON_PATH, 'w') as outfile:
			json.dump(pages, outfile)

	i += 1

with open(JSON_PATH, 'w') as outfile:
	json.dump(pages, outfile, indent=4)

print "Done"
