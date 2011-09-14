Description
====================
TurboTequila is a Turbogears application with Tequila enabled.

First use
=====================
Download the project :

    $ git clone git://github.com/bbcf/pygdv.git.

(It will create a directory named 'pygdv')

You want to use another one for your installation, so choose a name for your project (myCoolProject)
and run the following commands :

    $ find . -depth -name '*pygdv*' -execdir rename turbotequila mycoolproject {} \;

(will rename all files with 'pygdv' by 'myCoolProject')

then

    $ find . -type 'f' -name '*' -exec sed -i 's/pygdv/mycoolproject/' {} \;

(will rename all occurances of 'pygdv' in all files by 'myCoolProject')

``WARNING`` : Avoid using upper case with naming your project. Just use lower case and it will be fine.

In the future, we plan to avoid this by directly provide a plugin for Turbogears and a Tequila project will
be created by a simple command like 'paster quickstart tequila'.


Installation and Setup (example is given with a Fedora 15 (Lovelock))
======================

Install ``postgresql`` on your system::
su -c 'yum install postgresql postgresql-server'
see http://www.postgresql.org/docs/ for more.

Install the ``dev packages`` for postgresql, and the ``python bindings``::
    
    $ su -c 'yum install postgresql-devel python-psycopg2'

Create the database and change the adress in ``pygdv/development.ini`` under ``sqlalchemy.url``.

Install ``pygdv`` using the setup.py script::

    $ cd pygdv
    $ python setup.py install

Create the project database for any model classes defined::

    $ paster setup-app development.ini

Follow the instructions given.

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ paster serve --reload development.ini

Then you are ready to go.



 This code was written by the BBCF
 http://bbcf.epfl.ch/              
 webmaster.bbcf@epfl.ch            

