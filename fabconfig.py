from fabric.api import env

env.main_dir = '/var/www/vhosts/fantiago.com/sub.predictions/'
env.builds_dir = env.main_dir + 'builds'
env.web_dir = 'www'

def dev():
    "dev environment"
    env.build = 'dev'
    env.hosts = ['178.77.101.195']
    env.virtualenv = env.main_dir + 'virtualenvs/dev'
    env.code_dir = env.main_dir + 'builds/dev'
    env.apache_conf = 'deploy/apache/dev.conf'
    env.nginx_conf = 'deploy/nginx/dev.conf'
    env.wsgi = 'deploy/wsgi/dev.wsgi'

def stage():
    "stage environment"

def production():
    "production environment"
