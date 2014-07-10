#!/usr/bin/env python

import ez_epub
from lxml import html
from lxml.etree import Comment
import logging
import json
from genshi.input import HTML
import sys

class Chapter:

    def __init__(self):
        self.title = ''
        self.subsections = []
        self.css = ''
        self.text = []
        self.templateFileName = 'chapter.html'


JSON_PATH = 'scrape.json'

# TODO: use argparse?
convert_comments = False
if len(sys.argv) == 2 and sys.argv[1] == '--convert-comments':
    convert_comments = True
elif len(sys.argv) > 1:
    sys.exit('USAGE: {} [--convert-comments]'.format(sys.argv[0]))

logging.basicConfig()
logger = logging.getLogger("scraper")
logger.setLevel(logging.DEBUG)

with open(JSON_PATH, 'r') as outfile:
    pages = json.load(outfile)


book = ez_epub.Book()
book.title = "Ra"
book.authors = ["Sam Hughes"]
book.sections = []
book.impl.add_meta('source', 'http://qntm.org/ra')

for page in pages:
    print
    print page['title']
    print page['url']

    content = html.fromstring(page['text'])

    # Convert contents to actual tags or remove them
    for c in content.iter(Comment):
        if convert_comments:
            logger.warn('Converting commment to tag' )
            pre = content.makeelement('pre', {'class': 'converted-comment'})
            pre.text = c.text
            content.replace(c, pre)
        else:
            logger.warn('Removing commment' )
            c.getparent().remove(c)

    # Convert style="text-align: right" to class
    for tag in content.xpath("//*[starts-with(@style, 'text-align: right')]"):
        logger.debug('Converting "text-align: right" to class' )
        del tag.attrib['style']
        tag.attrib['class'] = 'text-right'

    # Convert style="text-align: center" to class
    for tag in content.xpath("//*[starts-with(@style, 'text-align: center')]"):
        logger.debug('Converting "text-align: center" to class' )
        del tag.attrib['style']
        tag.attrib['class'] = 'text-center'

    # Check for missed style attributes
    for tag in content.xpath("//*[@style]"):
        logger.warn('Found remaining style attribute' )
        sys.exit('Giving up')

    chapter = Chapter()
    chapter.html = HTML(html.tostring(content), encoding='utf-8')
    chapter.title = page['title']
    book.sections.append(chapter)

book.make(book.title + '.epub')
