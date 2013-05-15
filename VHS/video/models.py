from django.db import models

import os

# from libs.rwrapper.rwrapper import rwrapper
# from libs.rwrapper.rwrapper import fields
# from django.shortcuts import render_to_response
# from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
#
#
# class Episode(rwrapper):
#     _db_table = 'episode'
#     url = fields.CharField()
#     title = fields.CharField(max_length=60)
#     description = fields.CharField()
#     state = fields.IntegerField()

    # def save(request):
    #   table = MyTable(title=request.POST.get('title'), description=request.POST.get('description'))
    #   table.save()
    #
    #   return HttpResponseRedirect('/new-page/%s' % table.id)


class Profile(models.Model):
    user = models.OneToOneField(User, blank=True, unique=True)
    unique = models.CharField(max_length=32, db_index=True, null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk is None:
            self.unique = os.urandom(16).encode('hex')
        super(Profile, self).save()

    def get_absolute_url(self):
        return '/profile/'

    def get_feed_url(self):
        return reverse('feed_unique', args=(self.unique, ))