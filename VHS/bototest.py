#!/usr/bin/env python

import boto

GOOGLE_STORAGE = 'gs'
BUCKET = 'welovepublicservice'

uri = boto.storage_uri('', GOOGLE_STORAGE)
conn = uri.connect("GOOGQDMNVNIPP2MC2QWT", "QhHmJd+w1+i+JFwyY0AubgTdp0B/YJgr+c3axz8r")

if not bool([bool(x) for x in uri.get_all_buckets() if x.name == BUCKET]):
    uri = boto.storage_uri(BUCKET, GOOGLE_STORAGE)

    try:
        uri.create_bucket()
        print 'Successfully created bucket "%s"' % 'welovepublicservice'
    except boto.exception.StorageCreateError, e:
        print 'Failed to create bucket:', e

uri = boto.storage_uri(BUCKET + '/7976.mp4', GOOGLE_STORAGE)

uri.set_acl('public-read')

#for obj in uri.get_bucket():
#    print '%s://%s/%s' % (uri.scheme, uri.bucket_name, obj.name)
#    print '  "%s"' % obj.get_contents_as_string()


#filename = 'apa.txt'
#
#dst_uri = boto.storage_uri(
#    BUCKET + '/' + filename, GOOGLE_STORAGE)
#dst_uri.new_key().set_contents_from_filename('test.db')