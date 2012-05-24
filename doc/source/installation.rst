############
Installation
############

*********
RabbitMQ
*********

------------
Installation
------------
pyGDV need you to install RabbitMQ, the application's messaging system which allow you to configure 
how and where pyGDV tasks will be run.

See `Celery documentation <http://ask.github.com/celery/getting-started/broker-installation.html>`_ , 
a great explanation on how to install RabbitMQ.

-------
Running
-------

Start RabbitMQ with ::

    $ sudo rabbitmq-server
    or 
    $ sudo rabbitmq-server -detached (in detached mode)
    and 
    $ sudo rabbitmqctl stop (to stop rabbitMQ running)

-----
Setup
-----
Add an user for pyGDV, give him a password ::

    $ sudo rabbitmqctl add_user pygdvuser pygdvpasswd

Add a host ::

    $ sudo rabbitmqctl add_vhost pygdvhost

and give the user the right permissions ::

    $ sudo rabbitmqctl set_permissions -p pygdvhost pygdvuser ".*" ".*" ".*"


********************************
Virtualenv and Virtualenvwrapper
********************************
It is Highly recommended for any project in python.
`Virtualenv <http://pypi.python.org/pypi/virtualenv>`_ is an isolated environment that prevents version conflicts, permissions, ...
`Virtualenvwrapper <http://pypi.python.org/pypi/virtualenvwrapper>`_ is a tool that make it easier to work with virtualenv.

Once it's installed, create your environment with ::

    mkvirtualenv pygdv

You should see something like ::
    
    (pygdv) $

.. note :: All following steps will assume that you are on a right environment
       	     
*********************
Database installation
*********************
By default pyGDV uses SQLite database system. It means that no configuration is needed.

Note that you can change it to any other database system supported by SQLAlchemy : see `supported databases <http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html#supported-databases>`_.

So if you want to use another database like *postgresql* for instance, you also need to install the right python binding ::

    (pygdv) $ easy_install psycopg2 


******************
pyGDV Installation
****************** 

1. Clone pyGDV from it's *git repository* ::

    $ git clone git@github.com:bbcf/pygdv.git

.. note :: If you do not have git installed, please do so (instruction `here <http://git-scm.com/book/en/Getting-Started-Installing-Git>`_ or `here <http://lmgtfy.com/?q=installing+git+source+version+control>`_).


2. Put you on the right environment ::

    $ workon pygdv

3. Install some dependencies ::

    (pygdv) $ easy_install -i http://tg.gy/215 tg.devtools
    (pygdv) $ easy_install numpy

.. note :: Theses steps are separated from the *normal* installation steps to prevent version conflicts


4. Install BBCF dependencies, *bbcflib* and *track*.
    You have to clone them somewhere ::
    
        (pygdv) $ git clone git@github.com:bbcf/bbcflib.git
        (pygdv) $ git clone git@github.com:bbcf/track.git	
  
    And add them to your virtualenv (or PYTHONPATH) ::

        (pygdv) $ add2virtualenv /path/where/you/cloned/bbcflib
        (pygdv) $ add2virtualenv /path/where/you/cloned/track

5. Install pygdv ::

        (pygdv) $ cd pygdv
        (pygdv) $ python setup.py develop



***********
pyGDV setup
***********

After theses steps are finished, you must build the database by launching the command ::

    (pygdv) $ paster setup-app developement.ini

.. warning :: proxy-prefix must not be on the configuration file when you run that command



