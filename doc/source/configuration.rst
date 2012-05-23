*******************
pyGDV Configuration
*******************
There is three different configurations files to edit. Yes it is a lot, but your running a webserver that will launch 
some costly computationnal tasks ;)

You need to carrefully read these files, but importants notes are gathered here : 

----------------
developement.ini
----------------
*Main server configuration*::

    [server:main] 
    host = localhost
    port = 8080 # choose the port to run pygdv on 
     
    [sa:auth]
    cookie_secret = 517cc2e0-acc0-4791-8ad2-1c3e952d34d5 # change it      

    [app:main]

     main.proxy = the url where your application can be contacted 
     plugin.service.url = the url where to contact the plugin service (joblauncher)
     sqlalchemy.url = `the connector of your database`
     set debug = false
     admin.mails = [a list of admins identified by their mails]



If you want to serve pyGDV behind a prefix, you can add at the end of the [app:main] section theses lines ::
    
    filter-with = proxy-prefix

    [filter:proxy-prefix]
    use = egg:PasteDeploy#prefix
    prefix = /myPrefix

.. warning :: before adding these lines, you must *deploy the application*.

.. tip :: You could rename this file as *production.ini*, it's a good practice to have diferents configuration files for different purposes.


-------
who.ini
-------
The authentication file ::

    [plugin:ticket]
    secret = change it
    serv_ul = put here the url where pyGDV can be contacted


---------------
celeryconfig.py
---------------
The tasks configuration. Many parameters can be added there. To know more about it go to `Celery doc <http://celery.readthedocs.org/en/latest/configuration.html>`_::
    
    CELERY_RESULT_DBURI = 'sqlite:///mydb.db' (the same as sqlalchemy.url in your webserver configuration file ~ developement.ini).
    BROKER_URL = 'amqp://pygdvuser:pygdvpassword@localhost:5672/pygdvhost' (the url you configurated with RabbitMQ).
