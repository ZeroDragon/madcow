#!/usr/bin/env python

"""NEVAR FORGET"""

import re
from include import rssparser
from include.utils import Base, UserAgent, stripHTML
from include.BeautifulSoup import BeautifulSoup
import os
import sys

__version__ = '0.2'
__author__ = 'cj_ <cjones@gruntle.org>'
__license__ = 'GPL'
__format__ = 'Terror: %s, DoomsDay: %s, IranWar: %s, IraqWar: %s, BodyCount: %s'

class Terror(Base):
    _url = 'http://www.dhs.gov/dhspublic/getAdvisoryCondition'
    _re_level = re.compile(r'<THREAT_ADVISORY CONDITION="(\w+)" />')
    _color_map = {
        'severe': 5,
        'high': 4,
        'elevated': 8,
        'guarded': 12,
        'low': 9,
    }

    def __init__(self, ua):
        self.ua = ua

    def level(self):
        try:
            doc = self.ua.fetch(Terror._url)
            level = Terror._re_level.search(doc).group(1)
            color = Terror._color_map[level.lower()]
            return '\x03%s,1\x16\x16%s\x0f' % (color, level)
        except Exception, e:
            print >> sys.stderr, 'error in %s: %s' % (self.__module__, e)
            return 'UNKNOWN'


class DoomsDay(Base):
    _url = 'http://www.thebulletin.org/minutes-to-midnight/'
    _re_time = re.compile(r'<div class="module-content"><h3>(.*?)</h3>')

    def __init__(self, ua):
        self.ua = ua

    def time(self):
        try:
            doc = self.ua.fetch(DoomsDay._url)
            time = DoomsDay._re_time.search(doc).group(1)
            return time
        except Exception, e:
            print >> sys.stderr, 'error in %s: %s' % (self.__module__, e)
            return 'UNKNOWN'


class IranWar(Base):
    _url = 'http://www.areweatwarwithiran.com/rss.xml'

    def war(self):
        try:
            rss = rssparser.parse(IranWar._url)
            return rss['items'].pop(0)['title']
        except Exception, e:
            print >> sys.stderr, 'error in %s: %s' % (self.__module__, e)
            return 'UNKNOWN'


class IraqWar(Base):
    _war_url = 'http://areweatwarwithiraq.com/rss.xml'
    _bodycount_url = 'http://www.iraqbodycount.org/'
    _re_whitespace = re.compile(r'\s+')

    def __init__(self, ua):
        self.ua = ua

    def war(self):
        try:
            rss = rssparser.parse(IraqWar._war_url)
            return rss['items'].pop(0)['title']
        except Exception, e:
            print >> sys.stderr, 'error in %s: %s' % (self.__module__, e)
            return 'UNKNOWN'

    def bodycount(self):
        try:
            doc = self.ua.fetch(IraqWar._bodycount_url)
            soup = BeautifulSoup(doc)
            data = soup.find('td', attrs={'class': 'main-num'})
            data = data.find('a')
            data = str(data.contents[0])
            data = stripHTML(data)
            data = IraqWar._re_whitespace.sub(' ', data)
            data = data.strip()
            return data
        except Exception, e:
            print >> sys.stderr, 'error in %s: %s' % (self.__module__, e)
            return 'UNKNOWN'


class Main(Base):
    enabled = True
    pattern = re.compile('^\s*(?:terror|doomsday|war)\s*$', re.I)
    require_addressing = True


    help = 'terror - NEVAR FORGET'

    def __init__(self, madcow=None):
        self.ua = UserAgent()
        self.terror = Terror(ua=self.ua)
        self.doom = DoomsDay(ua=self.ua)
        self.iran = IranWar()
        self.iraq = IraqWar(ua=self.ua)

    def response(self, nick, args, **kwargs):
        try:
            return __format__ % (self.terror.level(), self.doom.time(),
                    self.iran.war(), self.iraq.war(), self.iraq.bodycount())
        except Exception, e:
            return '%s: problem with query: %s' % (nick, e)


def main():
    try:
        main = Main()
        args = main.pattern.search(' '.join(sys.argv[1:])).groups()
        print main.response(nick=os.environ['USER'], args=args)
    except Exception, e:
        print 'no match: %s' % e

if __name__ == '__main__':
    sys.exit(main())
