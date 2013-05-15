import os

a = (
    ['APA', 'asas'],
    ['BROKER_HOST', 'localhost'],
    ['BROKER_PORT', '6379'],
    ['SESSION_COOKIE_DOMAIN', 'localhost']
#    ['BROKER_HOST', '127.0.0.1'],
)

for item in a:
    os.environ[item[0]] = item[1]