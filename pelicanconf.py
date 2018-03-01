#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Fix for ipynb plugin https://github.com/danielfrg/pelican-ipynb/issues/49
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

AUTHOR = u'Serafeim Papastefanos'
SITENAME = u'/var/'
SITESUBTITLE =u'Various programming stuff'
SITEURL = 'https://spapas.github.io'
TIMEZONE = 'Europe/Athens'
DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_RSS = None
CATEGORY_FEED_RSS = None
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

# Blogroll
#LINKS =  (('Pelican', 'http://getpelican.com/'),
#          ('Python.org', 'http://python.org/'),
#          ('reStructuredText', 'http://docutils.sourceforge.net/rst.html'),
#)

#MENUITEMS = LINKS

# Social widget
#SOCIAL = (
    #('You can add links in your config file', '#'),
    #('Stackoverflow profile', 'http://stackoverflow.com/users/119071/serafeim'),
#)

DEFAULT_PAGINATION = 5
STATIC_PATHS  = ['images',]

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
TYPOGRIFY  = True
THEME = "../pelican-octopress-theme"
TWITTER_USERNAME='_serafeim_'
TWITTER_TWEET_BUTTON=True
#GOOGLE_ANALYTICS='UA-44750952-1'
GOOGLE_UNIVERSAL_ANALYTICS='UA-44750952-1'

PLUGIN_PATHS = ['../pelican-plugins']
PLUGINS = [
    'sitemap',
    'pelican_jsfiddle',
    'ipynb.markup',
]

SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'weekly',
        'pages': 'monthly'
    }
}

MARKUP = ('rst', 'md', 'ipynb', )
#MARKUP = ('rst', 'md', )
IGNORE_FILES = ['.ipynb_checkpoints']

GITHUB_USER = 'spapas'
GITHUB_SHOW_USER_LINK = True
GITHUB_SKIP_FORK = True