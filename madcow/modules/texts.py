#!/usr/bin/env python

"""Texts from last night"""


import random
import re
from BeautifulSoup import BeautifulSoup
from madcow.util.http import getsoup
from madcow.util import stripHTML
from madcow.util import Module
import re

__version__ = '0.1'
__author__ = 'Chris Jones <cjones@gruntle.org>'

url = 'http://www.textsfromlastnight.com/random/'
spam_re = re.compile(r'\s*http://tfl.nu/.*$')

class Main(Module):

    pattern = re.compile(r'^\s*(?:txt|texts|tfln)\s*$', re.I)
    help = 'txt - random texts from last night'

    def response(self, nick, args, kwargs):
        try:
            return u'%s: %s' % (nick, get_text())
        except Exception, error:
            self.log.warn(u'error in module %s' % self.__module__)
            self.log.exception(error)
            return u'%s: %s' % (nick, error)


def get_text():
    text = random.choice(getsoup(url).body.find('ul', id='texts-list')('div', 'text')).textarea
    return spam_re.sub(u'', text.renderContents().decode('utf-8'))


if __name__ == u'__main__':
    from madcow.util import test_module
    import sys
    sys.argv.append('txt')
    test_module(Main)
