from django import template
import datetime
register = template.Library()    

@register.filter('timestamp_to_time')
def convert_timestamp_to_time(timestamp):
    import time
    return datetime.date.fromtimestamp(int(timestamp))



@register.filter('int_to_boostraptable')
def convert_int_to_boostraptable(num):

    print 'num', num

    num = int(num)

    if num == 1:
        return 'warning'
    if num == 2:
        return 'success'