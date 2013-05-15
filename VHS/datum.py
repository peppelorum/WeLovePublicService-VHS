# -*- coding: utf-8 -*-

import os
import requests
from bs4 import BeautifulSoup
from sys import stdout
#from datetime import datetime, timedelta
from pytz import timezone, utc
#from django.utils.timezone import utc
from django.utils.timezone import datetime, timedelta, make_aware
from annoying.functions import get_config
from pyquery import PyQuery





def numerics(s):
    n = 0
    for c in s:
        if not c.isdigit():
            return n
        else:
            n = n * 10 + int(c)
    return n


def stripAllTags( html ):
    if html is None:
        return None
    return ''.join( BeautifulSoup( html ).findAll( text = True ) )


def parse_date(grej, typ):
    grej = unicode(grej)
    tz = timezone(get_config('TIME_ZONE', None))
    hoj = datetime.utcnow().replace(tzinfo=tz)
    if grej.find('dag') != -1:
        days = numerics(grej)
        if typ == '+':
            ret = hoj + timedelta(days=days)
        else:
            ret = hoj - timedelta(days=days)
    elif grej.find('tim') != -1:
        hours = numerics(grej)
        if typ == '+':
            ret = hoj + timedelta(hours=hours)
        else:
            ret = hoj - timedelta(hours=hours)
    else:
        return hoj

    return ret


article = '<article class="svtUnit svtNth-1 svtMediaBlock playPositionRelative playJsInfo-Core playJsInfo-Hover playIEFixedHeight" data-title="Hurra för Kalle - Bubbel trubbel" data-description="Richard Scarrys äventyrsvärld är tillbaka med katterna Kalle och Katty, daggmasken Dagge och många av deras vänner.  Denna gång löser de roliga…" data-length="12 min" data-available="17 dagar kvar" data-broadcasted="tor 31 jan" data-published="" data-broadcaststarttime=""> \
						<div class="playDisplayTable"> \
				<a href="/video/254265/bubbel-trubbel" class="playLink playBoxWithClickArea playIELinkFix"> \
					<div> \
						<div class="svtMBFig-L-O-O-O svtMediaBlockFig-L playJsInfo-ImageContainer playPositionRelative"> \
							<img class="playGridThumbnail" alt="Hurra för Kalle - Bubbel trubbel" src="http://www.svt.se/barnkanalen/cachable_image/1359434280000/incoming/article254260.svt/ALTERNATES/medium/default_title"> \
													</div> \
						<span class="playDisplayTouch-N-I-I-I playJsInfo-Open playIconInline playIcon-ArrowDown playFloatRight"></span> \
						<h5 class="playGridHeadline"> \
															Bubbel trubbel \
																				</h5> \
													<p class="svtXColorWhite">Sändes: \
								<time datetime="2013-01-31T11:20+01:00"> \
								tor 31 jan \
								</time> \
							</p> \
																	</div> \
				</a> \
				<a href="?" class="playClickArea playJsInfo-Open" tabindex="-1"> \
					<span class="playIconInline playIcon-ArrowDown svtHide-Gte-S"></span> \
				</a> \
			</div> \
		</article>'


a = PyQuery(article)


print a.find('a.playLink').attr('href')

print a.find('time').attr('datetime')


# available = parse_date(article['data-available'], '+')
# length = article['data-length']
# broadcasted = parse_date(article['data-broadcasted'], '-')
# thumbnail = episode.select('img.playGridThumbnail')[0]['src']