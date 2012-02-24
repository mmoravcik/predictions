# Template fabric deployment file for deploying Git projects
#
# Installation
# ------------
#
# To use this file, copy it into the root of your project and set up a configuration
# file fabconfig.py. It should define functions for each environment that will update
# the 'env' global. Here's a sample implementation:
#
# from fabric.api import env
#
# env.builds_dir = '/var/www/carlsberg/cdk/builds'
# env.web_dir = 'www'
# env.test_apps = 'shop'
#
# def dev():
# "Sets the dev environment"
# env.build = 'dev'
# env.hosts = ['192.168.125.95']
# env.virtualenv = '/var/www/carlsberg/cdk/virtualenvs/dev'
# env.code_dir = '/var/www/carlsberg/cdk/builds/dev'
# env.apache_conf = 'deploy/apache/carlsberg-cdk-dev.conf'
# env.wsgi = 'deploy/apache/carlsberg-cdk-dev.wsgi'
#
# def stage():
# "Sets the stage environment"
# env.build = 'stage'
# env.hosts = ['192.168.125.95']
# env.virtualenv = '/var/www/carlsberg/cdk/virtualenvs/stage'
# env.code_dir = '/var/www/carlsberg/cdk/builds/stage'
# env.apache_conf = 'config/carlsberg-cdk-stage.conf'
# env.wsgi = 'config/carlsberg-cdk-stage.wsgi'
#
# def production():
# "Sets the production environment"
# env.build = 'production'
# env.hosts = ['192.168.125.96']
# env.virtualenv = '/var/www/carlsberg/cdk/virtualenvs/production'
# env.code_dir = '/var/www/carlsberg/cdk/builds/production'
# env.apache_conf = 'config/carlsberg-cdk-production.conf'
# env.wsgi = 'config/carlsberg-cdk-production.wsgi'
#
# Usage
# -----
#
# This file is designed so projects can be deployed from a developer's laptop, you
# don't need to SSH into the remote server. The only requirements are that you
# have a SSH user with sudo privileges.
#
# To deploy to a particular environment, use:
#
# $ fab dev deploy # dev deployment
# $ fab production deploy # production deployment
#
# Each of these commands sets up the appropriate environment, then runs the generic
# deploy method that uses these settings.
#
# Deployment strategy
# -------------------
#
# The 'deploy' target does the following:
#
# 1. Updates the specified branch to the latest commit from the remote Git repo
# 2. Creates a tarball in /tmp
# 3. Uploads the tarball to the remote server
# 4. Unpacks the tarball into the correct places on the remote server. This includes:
# - Creating a new build folder and symlinking to it
# - Deleting any unnecessary files
# - Copying the apache config into place
# - Copying cronjobs into place
# - Touching the WSGI file to reload the new python code
# - Cleaning up

import datetime
import os

from fabric.api import local, run, sudo, env
from fabric.colors import green, red
from fabric.context_managers import cd, lcd
from fabric.operations import put, prompt

from fabconfig import *


# Deployment tasks

def deploy(branch='master', repo='origin'):
    """
Deploy to a environment

This is the main task for deployment.
"""

    # Ensure we have the latest code
    update_codebase(branch, repo)
    
    
    commit_id = _get_commit_id()

    # Versioning: we always deploy from a tag so we either select one
    # or create one.
    print green("Fetching latest tags")
    local('git fetch --tags')
    local('git tag | tail -5')
    env.version = prompt('Enter tag to deploy from [if new, then the tag will be created]')
    assert len(env.version) > 0

    # Create tag if it is new
    output = local('git tag -l %s' % env.version, capture=True)
    output = output.strip()
    if len(output) == 0:
        print green("Tagging version '%s'" % env.version)
        local('git tag %s' % env.version)
        local('git push --tags')
    else:
        print green("Deploying from tag %s" % env.version)

    # Create file of code to deploy
    archive_file = '/tmp/build-%s.tar.gz' % env.version
    prepare_build(archive_file)

    # Determine user to use for deployment
    env.user = prompt('Username for remote host? [default is current user] ') or os.environ['USER']

    # Upload and deploy
    upload(archive_file)
    
    unpack(archive_file, commit_id, branch)

    # Dependencies
    update_virtualenv()

    # Database, static, i18n
    migrate_schema()
    #collect_static_files()
    #collect_messages()

    # Server configuration
    _deploy_apache_config()
    _deploy_nginx_config()
    #deploy_cronjobs()
    #_deploy_cronjobs()
    nginx_reload()
    apache_reload()
    restart()
    delete_old_builds()
    #whoosh_setup()

def _get_commit_id():
    "Returns the commit ID for the branch about to be deployed"
    return local('git rev-parse HEAD', capture=True)[:20]

def update_codebase(branch='master', repo='origin'):
    """
Pull latest code
"""
    print(green('Updating codebase from remote "%s", branch "%s"' % (repo, branch)))
    local('git checkout %s' % (branch))
    local('git pull %s %s' % (repo, branch))

def prepare_build(archive_file, reference='master'):
    """
Creates a gzipped tarball with the code to be deployed.
"""
    local('git archive --format tar %s %s | gzip > %s' % (reference, env.web_dir, archive_file))

def upload(local_path, remote_path=None):
    """
Upload a file to the remote server
"""
    if not remote_path:
        remote_path = local_path
    print green("Uploading %s to %s" % (local_path, remote_path))
    put(local_path, remote_path)

def unpack(archive_path, commit_id, branch):
    """
Unpacks the tarball into the correct place
"""

    # We use a build folder that includes the date and time.
    print green("Creating build folder")
    now = datetime.datetime.now()
    env.build_dir = '%s-%s' % (env.build, now.strftime('%Y-%m-%d-%H-%M'))
    with cd(env.builds_dir):
        # Unpack
        sudo('tar xzf %s' % archive_path)
        
        # Remove some unnecessary files
        #sudo('rm %(web_dir)s/settings_test.py' % env)

        # Create new build folder (which isn't symlinked in yet)
        sudo('if [ -d "%(build_dir)s" ]; then rm -rf "%(build_dir)s"; fi' % env)
        sudo('mv %(web_dir)s %(build_dir)s' % env)

        # Append release info to settings.py. This requires having a setting
        # set to "UNVERSIONED" in settings.py, which gets substituted here.
        sudo("sed -i 's/UNVERSIONED/%(version)s/' %(build_dir)s/settings.py" % env)

        # Create new symlink
        sudo('if [ -h %(build)s ]; then unlink %(build)s; fi' % env)
        sudo('ln -s %(build_dir)s %(build)s' % env)

        # Add file indicating Git commit
        sudo('echo -e "branch: %s\ntag: %s\nuser: %s" > %s/build-info' % (branch, env.version, env.user, env.build))

        # Remove uploaded file
        sudo('rm %s' % archive_path)
    
def update_virtualenv():
    """
Updated dependencies
"""
    with cd(env.code_dir):
        sudo('source %s/bin/activate && pip install -q -r deploy/requirements.txt' % env.virtualenv)

def migrate_schema():
    """
Apply any migrations
"""
    with cd(env.code_dir):
        sudo('source %s/bin/activate && ./manage.py syncdb && ./manage.py migrate' % env.virtualenv)

def collect_static_files():
    """
Collect all static files into the public folder so they can be served
by nginx
"""
    with cd(env.code_dir):
        sudo('source %s/bin/activate && ./manage.py collectstatic --noinput > /dev/null' % env.virtualenv)

def _deploy_apache_config():
    "Deploys the apache config"
    print green('Moving apache config into place')
    with cd(env.builds_dir):
        sudo('mv %(build)s/%(apache_conf)s /etc/apache2/sites-available/' % env)

def _deploy_nginx_config():
    print green('Moving nginx config into place')
    with cd(env.builds_dir):
        sudo('mv %(build)s/%(nginx_conf)s /etc/nginx/sites-available/' % env)
    


def _deploy_cronjobs():
    "Deploys the cron jobs"
    print green('Deploying cronjobs')
    with cd(env.builds_dir):
        sudo('if [ $(ls %(build)s/cron.d) ]; then mv %(build)s/cron.d/* /etc/cron.d/; fi' % env)

def restart():
    "Reloads python code"
    print green('Touching WSGI file to reload python code')
    with cd(env.builds_dir):
        sudo('touch %(build)s/%(wsgi)s' % env)

def delete_old_builds():
    print green('Deleting old builds')
    with cd(env.builds_dir):
        sudo('find . -maxdepth 1 -type d -name "%(build)s*" | sort -r | sed "1,3d" | xargs rm -rf' % env)

def apache_reload():
    "Reloads apache config"
    sudo('/etc/init.d/apache2 force-reload')

def apache_restart():
    "Restarts apache"
    sudo('/etc/init.d/apache2 restart')

def nginx_reload():
    "Reloads nginx config"
    sudo('/etc/init.d/nginx force-reload')

def nginx_restart():
    "Restarts nginx"
    sudo('/etc/init.d/nginx restart')

def apache_configtest():
    "Checks apache config syntax"
    sudo('/usr/sbin/apache2ctl configtest')

def nginx_configtest():
    "Checks nginx config syntax"
    sudo('/usr/sbin/nginx -t')
    
def whoosh_setup():
    "setup the whoosh's search engine permissions"
    print green('Setting up whoosh')
    with cd(env.code_dir):
        sudo("chown root:www-data -R whoosh/recipes_index")
        sudo("sudo chmod 775 -R whoosh/recipes_index")

