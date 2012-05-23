###########
Start pyGDV
###########

In order to have the application running, you must have RabbitMQ running before.

Then you can start the webserver and the worker.

.. warning :: If you use daemon files, you must edit them. Some parameters are mandatory.


***************
Start webserver
***************

You can start pyGDV with ::

    (pygdv) $ paster serve --reload devlopement.ini

or by using the daemon file provided

   (pygdv) $ webserverctl start

*************
Start worker
*************

Use ::

    (pygdv) $ celeryd --loglevel=DEBUG

Or use the daemon file ::

    (pygdv) $ workerctl start

