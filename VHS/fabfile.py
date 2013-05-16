# Copyright 2011 Henri Siponen, Armens Movsesjans, Panu Salmi
# License: GNU General Public License, version 2 or later

#from __future__ import absolute_import
#from __future__ import with_statement

from fabric.api import *
import socket
import paramiko
from random import choice
import string
import time
import os
from fabric.contrib import django, files
django.settings_module('VHS.settings')
from django.conf import settings as django_settings
from annoying.functions import get_config
from deploy.utils import virtualenv, mpath, import_celeryconfig

from fabtools import require
import fabtools


env.user = 'vhs'
#env.password = 'harijung'
env.port = 2000
env.release = time.strftime('%Y%m%d%H%M%S')
env.roledefs = {
    'ffmpeg' : [
#    '10.211.55.8',
#    '10.211.55.9',
    '141.255.184.75',
    ],
    'web': [
        '109.74.0.11',
    ]
}

@task
@roles('web')
def web_setup_user():
    # user = env.user
    env.user = 'wlps'
    user = prompt('Enter a new username:')
    password = prompt('Enter a new password for user %s:' % user)
    require.user(user, shell='/bin/bash', password=password)
    fabtools.require.users.sudoer(user, hosts='ALL', operators='ALL', passwd=False, commands='ALL')


@task
@roles('web')
def web_new_database():
    db = prompt('Enter a new database:')
    user = prompt('Enter a new username:')
    require.postgres.database(db, user, locale='sv_SE.UTF-8')



@task
@roles('web')
def web_setup():
    sudo('apt-get -u update')
    sudo('apt-get -y dist-upgrade')

    require.deb.packages([
        'python-virtualenv',
        'supervisor',
        'gcc',
        'python-dev',
        'vim',
        'postgresql',
        'libpq-dev',
        'libxml2-dev',
        'libxslt1-dev',
    ])

    install('gcc')
    install('make')

    with cd('/etc/apt/'):
        if not files.contains('sources.list', 'http://packages.dotdeb.org'):
            sudo('echo deb http://packages.dotdeb.org squeeze all >> sources.list')

        if not files.contains('sources.list', 'rethinkdb'):
            sudo('echo deb http://ppa.launchpad.net/rethinkdb/ppa/ubuntu lucid main >> sources.list')


    install('rethinkdb')

    #
    # deb http://ppa.launchpad.net/rethinkdb/ppa/ubuntu lucid main
    # deb-src http://ppa.launchpad.net/rethinkdb/ppa/ubuntu lucid main

    run('wget http://www.dotdeb.org/dotdeb.gpg')
    run('cat dotdeb.gpg | sudo apt-key add -')

    # run('gpg --keyserver pgpkeys.mit.edu --recv-key 135D945A11D62AD6')
    # run('gpg -a --export 135D945A11D62AD6 | apt-key add -')

    db = prompt('Enter a new database:')
    user = prompt('Enter a new username:')
    password = prompt('Enter a new database password for user %s:' % user)
    # Require a PostgreSQL server
    require.postgres.server()
    require.postgres.user(user, password)
    require.postgres.database(db, user, locale='sv_SE.UTF-8')

    # Require a supervisor process for our app
    require.supervisor.process('vhs',
                               command='/home/vhs/ost/bin/gunicorn_django -c /home/vhs/ost/gunicorn_conf.py',
                               directory='/home/vhs/ost/VHS/',
                               user='vhs'
    )

    # Require an nginx server proxying to our app
    require.nginx.proxied_site('sys.vhs.local',
        docroot='/home/vhs/ost/VHS/static/',
        proxy_url='http://127.0.0.1:8001'
    )

    if not files.exists(django_settings.RQ_DEPLOY_PATH):
        run('virtualenv %s' % django_settings.RQ_DEPLOY_PATH)
    #        run('pip install gunicorn')

    # worker_deploy()

@task
@roles('web')
def cron():
    fabtools.cron.add_daily('crawl', 'vhs', 'cd /home/vhs/ost/VHS/ && /home/vhs/ost/bin/python /home/vhs/ost/VHS/manage.py indexapi')
    # fabtools.cron.add_daily('httpstatus', 'wlps', 'cd /home/vhs/ost/VHS/ && /home/vhs/ost/bin/python /home/vhs/ost/VHS/manage.py httpstatus')

def upload_tar_from_git():

    "Create an archive from the current Git master branch and upload it"
    git_dir = local('git rev-parse --show-toplevel', capture=True)
    with lcd(git_dir):
        local('git archive --format=tar master | gzip > %s.tar.gz' % env.release)
        with virtualenv(django_settings.RQ_DEPLOY_PATH):
            put('%s.tar.gz' % env.release, 'release.tar.gz')
            run('tar zxf release.tar.gz')
            run('rm release.tar.gz')
        local('rm %s.tar.gz' % env.release)


@task
@roles('web')
def web_deploy():
    upload_tar_from_git()

    with virtualenv(django_settings.RQ_DEPLOY_PATH):
        run('ls')
        run('pip install -r VHS/requirements.txt')

        run('python VHS/manage.py syncdb')
        run('python VHS/manage.py migrate')
        run('python VHS/manage.py collectstatic --noinput')

#    with cd(django_settings.RQ_DEPLOY_PATH):
        run('source bin/activate')

#        run('ls')

#    with cd(django_settings.RQ_DEPLOY_PATH):
#        with cd('VHS'):
#            run('ls')
#            run('python manage.py migrate')


    run('sudo supervisorctl restart vhs')
#
#        run('mkdir VHS')
#        put('VHS', 'VHS')
#
#        run('pip install ')

@task
@roles('ffmpeg')
def worker_setup():
    with cd('/etc/apt/'):
        if not files.contains('sources.list', 'http://ftp.sunet.se/pub/os/Linux/distributions/debian-multimedia/'):
            sudo('echo deb http://ftp.sunet.se/pub/os/Linux/distributions/debian-multimedia/ stable main >> sources.list')

    sudo('apt-get -u update')
    sudo('apt-get install --force-yes -y deb-multimedia-keyring')
    with settings(warn_only=True):
        sudo('apt-get remove ffmpeg x264 libav-tools libvpx-dev libx264-dev yasm')
    sudo('apt-get -y install autoconf build-essential checkinstall git libass-dev libfaac-dev libgpac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev librtmp-dev libtheora-dev libtool libvorbis-dev pkg-config texi2html zlib1g-dev')
    sudo('apt-get -y dist-upgrade')
    install('ffmpeg')
    install('screen')
    install('python-virtualenv')
    install('vim')
    install('autossh')
    install('ntp')

    put('deploy/installffmpeg.sh', 'installffmpeg.sh', mode=0755)
    sudo('./installffmpeg.sh')

    if not files.contains('.ssh/config', 'Host %s' % env.roledefs['web'][0]):
        print 'yay'

    if not files.contains('.ssh/config', env.roledefs['web'][0]):
        files.append('.ssh/config', 'Host %s' % env.roledefs['web'][0])
        files.append('.ssh/config', 'HostName %s' % env.roledefs['web'][0])
        files.append('.ssh/config', 'Port %s' % env.port)
        files.append('.ssh/config', 'IdentityFile /home/%s/worker.rsa' % env.user)

    if not files.exists('worker.rsa.pub'):
        run('ssh-keygen -f worker.rsa -t rsa -N ""')
        run('ssh-copy-id -i worker.rsa.pub %s@%s' % (env.user, env.roledefs['web'][0]))


#    dir = os.getcwd()
    get('worker.rsa.pub')
    local('ssh-copy-id -i worker.rsa.pub %s@%s' % (env.user, env.roledefs['web'][0]))
    sudo('/etc/init.d/ntp restart')

    if not files.exists(django_settings.RQ_DEPLOY_PATH):
        run('virtualenv %s' % django_settings.RQ_DEPLOY_PATH)

    worker_deploy()


@task
@roles('ffmpeg')
def get_key():
    dira = os.getcwd()
    get('worker.rsa.pub', dira)
    local('ssh-copy-id -i worker.rsa.pub %s@%s' % (env.user, env.roledefs['web'][0]))

@task
@roles('ffmpeg')
def worker_deploy():

    env.user = 'wlps'

    with virtualenv(django_settings.RQ_DEPLOY_PATH):

        for item in django_settings.RQ_PIP:
            run('pip install %s' % item)

        run('mkdir -p '+ django_settings.SVTGETSAVEFOLDER)

        for item in django_settings.RQ_SETTINGS_NEEDED:
            files.append('rq_settings.py', '%s=\'%s\'' % (item, get_config(item, 'FAIL!')))

        for item in django_settings.RQ_IMPORTS:

            if os.path.isdir(os.path.join(django_settings.ROOT_DIR, item[0])):
                #If the source is a directory, create same directory on the target
                run('mkdir -p '+ item[1])
            if item[1].find('/') != -1:
                #If the target filename contains a directory name, create that, and create a __init__.py
                run('mkdir -p '+ '/'.join(item[1].split('/')[:-1]))
                run('touch '+ '/'.join(item[1].split('/')[:-1]) + '/__init__.py')

            put(item[0], item[1])

@task
@roles('ffmpeg')
def worker_start():
    run('screen bash -c "source /home/vhs/ost/bin/activate; cd ost; python /home/vhs/ost/startrq.py"')


@task
@hosts('host1.local')
def init():
    """Initialise the server"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            setup_webserver()
            setup_squid()
            configure_reposource()
        user_add('simo','password')



@task
@roles('servers')
def install_video_reqs():
    install('ffmpeg')


@task
@roles('workstations')
@parallel
def main():
    """Main installation task for workstations"""
    with settings(linewise=True,warn_only=True):
        if is_host_up(env.host):
            point_to_proxy()
            user_add('simo','password')
            configure_reposource()
            sudo("software-properties-gtk -e universe")
            update()
            if run("ls /etc/gnome").failed:
                install('ubuntu-desktop')
		if local('ls awasebg.jpg').failed:
	                local("wget http://myy.haaga-helia.fi/~a0900094/awasebg.jpg")
                set_bg("awasebg.jpg")
                if local('ls heitero.ogg').failed:
			local("wget http://myy.haaga-helia.fi/~a0903751/heitero.ogg")
                set_soundgreeting("heitero.ogg")
		run('setxkbmap fi')
                reboot()    

@task
def cmd(command):
    """Pass a command to the hosts"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            run(command)

@task
def cmds(command):
    """Pass a sudo command to the hosts"""
    with settings(warn_only=True):
        if is_host_up(env.host):
            sudo(command)

@task
@parallel
def install(package):
    """Install a package"""
#    with settings(linewise=True, warn_only=True):
    if is_host_up(env.host):
        sudo("apt-get update")
        for retry in range(2):
            if sudo("apt-get -y install %s" % package).failed:
                local("echo INSTALLATION FAILED FOR %s: was installing %s $(date) >> ~/fail.log" % (env.host,package))
            else:
                break

@task
@parallel
def install_auto(package):
    """Install a package answering yes to all questions"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo('DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y %s' % package)

@task
@hosts('host1.local')
def install_apache():
    """Install Apache server with userdir enabled"""
    with settings(linewise=True, warn_only=True):
    	if is_host_up(env.host):
            sudo("apt-get update")
            sudo("apt-get -y install apache2")
            if run("ls /etc/apache2/mods-enabled/userdir.conf").failed:
            	sudo("a2enmod userdir")
            	sudo("/etc/init.d/apache2 restart")

@task
@parallel
def uninstall(package):
    """Uninstall a package"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get -y remove %s" % package)

@task
@parallel
def update():
    """Update package list"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")

@task
@parallel
def upgrade():
    """Upgrade packages"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo("apt-get -y upgrade")

@task 
@parallel
def upgrade_auto():
    """Update apt-get and Upgrade apt-get answering yes to all questions"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo('apt-get upgrade -o Dpkg::Options::="--force-confold" --force-yes -y')

@task
@parallel
@roles('workstations')
def upgrade_to_oneiric():
    """Upgrade Ubuntu natty distribution to oneiric"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            if not run('lsb_release -c') == 'Codename:    oneiric':
	         install_auto('oneiric-sources')
                 sudo("apt-get update")
                 sudo('DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get dist-upgrade -o Dpkg::Options::="--force-confold" --force-yes -y')
                 if local('ls awasebg.jpg').failed:
			local("wget http://myy.haaga-helia.fi/~a0900094/awasebg.jpg")
                 set_bg("awasebg.jpg")
                 if local('ls heitero.ogg').failed:
			local("wget http://myy.haaga-helia.fi/~a0903751/heitero.ogg")
                 set_soundgreeting("heitero.ogg")
                 sudo("reboot")

@task
@parallel
def user_add(new_user, passwd=False):
    """Add new user"""
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        if is_host_up(env.host):
	    if not passwd:
                passwd = generate_passwd()
            if not sudo("echo -e '%s\n%s\n' | adduser %s" % (passwd,passwd,new_user)).failed:
                if env.host=='host1.local': 
                    sudo("mkdir /home/%s/public_html" % new_user)
                    sudo("chown %s:%s /home/%s/public_html/" % new_user)

@task
@parallel
def user_passwd(user, passwd=False):
    """Change password for user"""
    with settings(hide('running', 'stdout', 'stderr'), warn_only=True):
        if is_host_up(env.host):
            if not passwd:
                passwd = generate_passwd()
            sudo("echo -e '%s\n%s' | passwd %s" % (passwd,passwd,user))

@task
@parallel
def user_delete(user):
    """Delete user"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("deluser %s" % user)

@task
def status():
    """Display host status"""
#    with settings(linewise=True,warn_only=True):
    if is_host_up(env.host):
        run("uptime")
        run("uname -a")

@task
@parallel
def shut_down():
    """Shut down a host"""
    if is_host_up(env.host):
        sudo("shutdown -P 0")

@task
@parallel
def reboot():
    """Reboot a host"""
    if is_host_up(env.host):
        sudo("shutdown -r 0")

@task
def file_put(localpath, remotepath):
    """Put file from local path to remote path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            put(localpath,remotepath)

@task
def file_get(remotepath, localpath):
    """Get file from remote path to local path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            get(remotepath,localpath+'.'+env.host)

@task
def file_remove(remotepath):
    """Remove file at remote path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("rm -r %s" % remotepath)

@task
@parallel
def configure_reposource():
    """Adds host1.local to repository list"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            with cd("/etc/apt/sources.list.d/"):
                sudo("echo deb http://172.28.212.1/~ubuntu/ natty main >> repository.list")
                # remove duplicates:
                sudo("sort -u repository.list > repository.list.new")
                sudo("cat repository.list.new > repository.list")
                sudo("rm repository.list.new")
        
@task
@parallel
def set_bg(bg):
    """Set an image file to be used as background"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            if local("ls %s" % bg).failed:
                local("echo image file not found")
            else:
                put(bg,"/usr/share/backgrounds/warty-final-ubuntu.png",use_sudo=True)

@task
@parallel
def set_soundgreeting(soundfile):
    """Set a sound file to be used on login"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            if local("ls %s" % soundfile).failed:
                local("echo sound file not found")
            else:
                put(soundfile,"/usr/share/sounds/ubuntu/stereo/dialog-question.ogg",use_sudo=True)

@hosts('host1.local')
def setup_webserver():
    with settings(warn_only=True):
    	install_apache()
        install('php5')
        setup_reprepro()
        clonegit()
        configure_reposource()
        add_to_repo()
        if run('ls /etc/apache2/mods-enabled/php5.conf.hng').failed:
             install_auto('php-enable-users')
             sudo("/etc/init.d/apache2 restart")
        run('mkdir backup')

@hosts('host1.local')
def clonegit():
    """Clones awaseConfigurations git source"""
    with settings(warn_only=True):
    	install('git')
	with cd('~/'):
        	run("git clone https://github.com/AwaseConfigurations/main")

@hosts('host1.local')
def add_to_repo():
    """Add sources to reprepro"""
    with settings(warn_only=True):
	with cd('~/public_html/'):
	        run("cp ~/main/packages/php/php-enable-users/php-enable-users_0.1_all.deb ~/public_html/")
                run("cp ~/main/packages/apt/add-unimulti/add-unimulti_0.1_all.deb ~/public_html/")
                run("cp ~/main/packages/apt/oneiric-sources/oneiric-sources_0.1_all.deb ~/public_html/")
                run("reprepro includedeb natty add-unimulti_0.1_all.deb")
                run("reprepro includedeb natty oneiric-sources_0.1_all.deb")
                if run("reprepro includedeb natty php-enable-users_0.1_all.deb").failed:
                    setup_reprepro()
                    clonegit()
                    run("cp ~/main/packages/php/php-enable-users/php-enable-users_0.1_all.deb ~/public_html/")
                    run("cp ~/main/packages/apt/add-unimulti/add-unimulti_0.1_all.deb ~/public_html/")
                    run("cp ~/main/packages/apt/oneiric-sources/oneiric-sources_0.1_all.deb ~/public_html/")
                    run("reprepro includedeb natty php-enable-users_0.1_all.deb")                    
                    run("reprepro includedeb natty add-unimulti_0.1_all.deb")
                    run("reprepro includedeb natty oneiric-sources_0.1_all.deb")

@hosts('host1.local')
def setup_squid():
    """Setups Squid for host1.local"""
    with settings(warn_only=True):
    	if run("ls /etc/squid/squid.conf").failed:
        	sudo("apt-get update")
                sudo("apt-get -y install squid")
                run("wget https://raw.github.com/AwaseConfigurations/main/master/squid/squid.conf")
                sudo("cp squid.conf /etc/squid/squid.conf")
                sudo("chown root:root /etc/squid/squid.conf")
                sudo("service squid restart")
            
@hosts('host1.local')
def setup_reprepro():
    """Setups reprepro for host1.local"""
    with settings(warn_only=True):
    	if run("ls ~/public_html/conf/").failed:
 		sudo("apt-get update")
                sudo("apt-get -y install reprepro")    
                run("wget https://raw.github.com/AwaseConfigurations/main/master/scripts/reprepro_setup.sh")
                run("chmod +x reprepro_setup.sh")
                run("./reprepro_setup.sh")
                run("rm reprepro_setup.sh")
                
@parallel
def point_to_proxy():
    with settings(warn_only=True):
    	sudo("""echo 'Acquire { Retries "0"; HTTP { Proxy "http://host1.local:3128"; }; };' | tee /etc/apt/apt.conf""")

def generate_passwd(length = 10):
    return ''.join(choice(string.ascii_letters + string.digits) for _ in range(length))

def is_host_up(host):
    """Verify the host computer is online before action"""
    print('Attempting connection to host: %s' % host)
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(1)
    host_up = True
    try:
        paramiko.Transport((host, 22))
    except Exception, e:
        host_up = False
        print('%s down, %s' % (host, e))
    finally:
        socket.setdefaulttimeout(original_timeout)
        return host_up

@task
@parallel
def smartmon_setup():
	"""Install and set up smartmontools"""
	with settings(warn_only=True):
        	if is_host_up(env.host):
			if run('ls /etc/smartmontools').failed:
				install_auto('smartmontools')
				sudo('smartctl -s on -o on -S on /dev/sda')

@task
def smartmon():
	"""SMART overall-health self-assesment test using smartmontools"""
	with settings(hide('running', 'user'), warn_only=True):
	        if is_host_up(env.host):
			smartmon_setup()
			sudo('smartctl -H /dev/sda | grep "test result"')

@task
def ssh_disable_passwd():
	"""Disable SSH password authentication"""
	with settings(hide('running', 'user'), warn_only=True):
	        if is_host_up(env.host):
			sudo('echo PasswordAuthentication no >> /etc/ssh/sshd_config')
			sudo('service ssh restart')

@task
def pubkey_distribute():
	""""Create a pair of keys (if needed) and distribute the pubkey to hosts"""
        with settings(warn_only=True):
                if is_host_up(env.host):
			if local('ls ~/.ssh/id_rsa.pub').failed:
				local('ssh-keygen -N "" -q -f ~/.ssh/id_rsa -t rsa')
				local('ssh-add')
			run('mkdir .ssh')
			file_put('~/.ssh/id_rsa.pub','/home/ubuntu/.ssh/authorized_copy')
			run('cat /home/ubuntu/.ssh/authorized_copy >> /home/ubuntu/.ssh/authorized_keys')
			local('sudo chown $(whoami):$(whoami) /etc/ssh/ssh_config')
			local('echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config')
			local('sudo chown root:root /etc/ssh/ssh_config')

@task
def dotdee_setup():
        """Install and set up dotdee"""
        with settings(warn_only=True):
                if is_host_up(env.host):
                        mystore = run('lsb_release -c')
                        if 'oneiric' in mystore:
                                install_auto('dotdee')
                        else:
                                print('You need to install Oneiric!')

@task
def dotdee_ssh_hosts():
        """Make dotdee path for ssh hosts"""
        with settings(warn_only=True):
                if is_host_up(env.host):
                        dotdee_setup()
                        if run ('ls /etc/dotdee').failed:
                                return
                        if run('ls .ssh/config').failed:
                                run('echo "" > .ssh/config')
                        sudo('dotdee --setup /home/ubuntu/.ssh/config')
                        run('ln -s /etc/dotdee/home/ubuntu/.ssh/config.d/ /home/ubuntu/.ssh/config.d')

@task
def dotdee_new(path):
        """Make dotdee path for files"""
        with settings(warn_only=True):
                if is_host_up(env.host):
                        dotdee_setup()
                        if run ('ls /etc/dotdee').failed:
                                return
                        if not run('ls %s' % path).failed:
                                sudo('dotdee --setup %s' % path)
                                sudo('ln -s /etc/dotdee%s.d/ %s.d' % (path,path,path))
                        else:
                                print('%s does not exist' % path)
