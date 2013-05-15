# -*- coding: utf-8 -*-


__author__ = 'peppe'


tmp = u'<span class="playMetaText"> \
<span><strong>SÃ¤ndes:</strong> <time datetime="2013-02-25T21:45+01:00">mån 25 feb</time>  -  </span> \
<span><strong>TillgÃ¤nglig till:</strong> mån 4 mar \
  -  </span> \
<span><strong>LÃ¤ngd:</strong> 10 min</span> \
</span> \
<span><strong>SÃ¤ndes:</strong> <time datetime="2013-02-25T21:45+01:00">mån 25 feb</time>  -  </span> \
<span><strong>TillgÃ¤nglig till:</strong> mån 4 mar \
  -  </span> \
<span><strong>LÃ¤ngd:</strong> 10 min</span> \
<span>Senaste nytt från Stockholms och Uppsala län. ABC sänder nyheter och väderprognoser. Kolla när du vill i SVT Play.</span> \
'

from bs4 import BeautifulSoup

from pyquery import PyQuery

def sanitize_html2(value):
    soup = PyQuery(value)
    soup = soup.remove('span.playMetaText')
    soup.remove('span.playMetaText')
    soup.remove('time')
    soup.remove('strong')

    return soup.html().split('<span>')[-1:]

print sanitize_html2(tmp)



# apa = PyQuery(tmp)
# a = apa.find('span')
#
# print a