#!/bin/bash 
# Created by Andre Anjos <andre.dos.anjos@cern.ch>
# Seg 14 Set 2009 16:49:23 CEST

export PYTHON=`which python2.5`
start_dir=`pwd`

source ./setup.sh
./install.sh

[ -d project ] && rm -rf project;
[ -d media ] && rm -rf media;
django-admin.py startproject project;
rm -f project/settings.py;
ln -s ../settings.py project/settings.py;
rm -f project/urls.py;
ln -s ../urls.py project/urls.py;

# base django project installation
cd project;
if [ ! -e db.sql3 ]; then
  ${PYTHON} manage.py syncdb --noinput;
  ${PYTHON} manage.py createsuperuser --email=andre.dos.anjos@gmail.com 
fi
mkdir templates;
ln -s ../../base.html templates/base.html;
cd ${start_dir};
mkdir media;
cd media;
ln -s ../sw/djangoogle*/djangoogle/media djangoogle;
ln -s ../sw/Django*/django/contrib/admin/media django;
svn co http://django-rosetta.googlecode.com/svn/trunk/rosetta/templates/rosetta rosetta
cd ${start_dir};

# update the translation strings
cd sw/djangoogle*/djangoogle;
django-admin.py compilemessages
cd ${start_dir};

# now run all tests
cd project;
${PYTHON} -m compileall .
${PYTHON} manage.py test djangoogle;
# and prepare the database for a manual inspection
${PYTHON} ../sw/djangoogle*/djangoogle/test_initial.py
# and let the webserver running
${PYTHON} manage.py runserver 8080;
cd ${start_dir};

