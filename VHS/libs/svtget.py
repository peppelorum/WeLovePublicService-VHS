# -*- coding: utf-8 -*-
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <p@bergqvi.st> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return. Peppe Bergqvist
# ----------------------------------------------------------------------------
#

import os
import sys

from BeautifulSoup import BeautifulSoup
import requests
import simplejson

import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from optparse import OptionParser

try:
    import rq_settings
except:
    print '**********************************'
    print 'rq_settings.py seems to be missing'
    print '**********************************'

def get_config(key, default):
    """
    Get settings from django.conf if exists,
    return default value otherwise

    example:

    ADMIN_EMAIL = get_config('ADMIN_EMAIL', 'default@email.com')
    """
    return getattr(rq_settings, key, default)


class Pirateget():

    def which(self, program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None

    def checkReqs(self):
        """
        Check that ffmpeg is installed
        """
        if not self.which('ffmpeg'):
            print 'ffmpeg seems not to be installed'
            sys.exit()

    def getVideo(self, url, tempfilename, filename):
        BUCKET = get_config('BUCKET', '')
        GOOGLE_STORAGE = get_config('GOOGLE_STORAGE', '')
        GS_KEY = get_config('GS_KEY', '')
        GS_SECRET = get_config('GS_SECRET', '')

        tempfilename = 'tmp'

#        filename = unicodedata.normalize('NFKD', filename).encode('ascii','ignore')
#        command = 'ffmpeg -i \"%s\" -acodec copy -vcodec copy -absf aac_adtstoasc -y "%s.mp4"' % (url, filename)

        # print 'filename', unicode(filename)
        command = 'ffmpeg -i \"%s\" -y "%s.mp4"' % (url, tempfilename)
        print command
        os.system(command)

        filename_gs = filename.split('/')[-1] + '.mp4'
        filename += '.mp4'
        tempfilename += '.mp4'
        conn = S3Connection(GS_KEY, GS_SECRET)
        bucket = conn.get_bucket('wlps')
        k = Key(bucket)
        k.key = filename_gs
        k.set_contents_from_filename(tempfilename)
        k.make_public()

        os.remove('tmp.mp4')

    def sort_by_age(self, d):
        '''a helper function for sorting'''
        try:
            import re
            quality = re.sub('[^0-9]', '', d['meta']['quality'].split('x')[0])
            return int(quality)
        except KeyError as inst:
            print('ERROR: %s' % inst)
#            logger.error('d: %s' % d)
            return inst

    def run(self, pk, title, url, folder, callback_url):
    # def run(self, id_, title,  url, path, filename, callback_url):

        filename = title

        if url.startswith("http://svt") or url.startswith("http://www.svt") is not True:
            print("Bad URL. Not SVT Play?")
            sys.exit()

        r = requests.get(url)
        soup = BeautifulSoup(r.content, convertEntities=BeautifulSoup.HTML_ENTITIES)

        if r.status_code == 404:
            print('ERROR: %s' % url)
            # raise Http404

        if not filename:
            try:
                filename = soup.find('title').text.replace(' | SVT Play', '')
            except:
                filename = 'could not parse'

        if folder:
            abspath = os.path.abspath(folder)
            filename = os.path.join(abspath, unicode(filename))

        video = requests.get('http://pirateplay.se/api/get_streams.js?url='+ url)
        # video = requests.get('http://10.211.55.2:8081/api/get_streams.js?url='+ url)

        json = simplejson.loads(video.content)
        try:
            json = sorted(json, key=self.sort_by_age, reverse=True)
            url = json[0]['url']
        except IndexError as inst:
            print('JSON-URL: %s' % json)

        self.getVideo(url, pk, filename)

        sent = requests.post(callback_url, data={'id': pk, 'key': get_config('CALLBACKKEY', '')})
        print 'Callback:', sent

        return True


def main():
    parser = OptionParser(usage="usage: %prog [options] url")
    parser.add_option("-p", "--path",
                      action="store", # optional because action defaults to "store"
                      dest="path",
                      default=False,
                      help="Path to save the MP4 to",)
    parser.add_option("-f", "--filename",
                      action="store", # optional because action defaults to "store"
                      dest="filename",
                      default=False,
                      help="Filename to save the MP4 to",)
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("wrong number of arguments")

    obj = Pirateget()
    obj.checkReqs()
    obj.run(args[0], options.path, options.filename)

if __name__ == '__main__':
    main()
