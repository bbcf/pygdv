Description
================================================================
GDV is a fast and easy to use genome browser. 
The main goal is to provide a tool for biologist and bioanalysts 
who wants to VISUALIZE and ANALYSE their data in an interactive and responding way.

Use
================================================================
A production version is running on [bbcf](http://gdv.epfl.ch/pygdv). 
You can log in if you have an account on [tequila](https://tequila.epfl.ch/) which is automatic if
you have a university account in Switzerland. If not, we will provide soon a demo version 
available for everybody. If you really wan't to test GDV, please sent a email to [bbcf webmaster](mailto:webmaster.bbcf@epfl.ch).


Installation
================================================================
pyGDV is written in python, so the recommended way of installing it (as all python modules)
is throught a virtual environment.
Here we put notes on installing [virtualenv](http://pypi.python.org/pypi/virtualenv) (will build your virtual environment)
& [virtualenvwrapper](http://pypi.python.org/pypi/virtualenvwrapper) (will make it easier to work with virtualenv).

Please refers to the official documentation if something goes wrong.

Virtualenv
----------------------------------------------------------------
1. Install devellopers packages (already done usually).
    * Xcode (MacOS)
    * python-dev & build-essential (Debian, Ubuntu)
    * python-devel (Fedor)

2. Install virtualenv
    sudo easy_install virtualenv


Virtualenvwrapper
----------------------------------------------------------------

1. Install python [pip](http://www.pip-installer.org/en/latest/index.html) (package manager)

2. Install vitualenvwrapper:
    pip install virtualenvwrapper

3. Define the directory that will contains your environements
    export WORKON_HOME=/usr/local/env (add in .bashrc)
    mkdir $WORKON_HOME

4. Execute virtualenwrapper.sh then source it
    source /usr/local/bin/virtualenvwrapper.sh (add in .bashrc)


5. Create the virtual environement that will contains GDV
    mkvirtualenv --no-site-packages -p python2.6 pygdv

You can now enter the virtual env with ``workon pygdv`` and exit with ``deactivate``


pyGDV
-----------------------------------------------------------------
It's not mandatory to install pyGDV on a virtualenv but it's recommended.


-- DRAFT --

1. Install git (do it throught your package manager)

2. Go to the directory where you want to install pyGDV.

3. Execute : 

	       git clone https://github.com/yjarosz/pygdv
   	       cd pygdv
	       python setup.py install
	       easy_install celery
	       easy_install webob==1.1.1
	       easy_install numpy
	       easy_install matplotlib
	       pip install -U kombu-sqlalchemy
	       

4. Install bbcflibs
   clone libraries bbcflib (git), bein (git), track (git), gMiner (git)
   a script will soon be provided to install them at once
   
5. Add them to the virtualenv
         
		add2virtualenv bbcflib
    		add2virtualenv track
    		add2virtualenv bein
    		add2virtualenv gMiner

6. copy developement ini file to make it for production
   ``cp development.ini production.ini``

7. enter info needed in production.ini

8. cp ``who.ini.sample who.ini``

9. fill who.ini

10. ``paster setup-app production.ini``

11. prefix your application if needed

12. enter the ip of the proxy if needed

13. run ``paster serve production.ini`

14. configure worker in ``celeryconfig.py``

15. run workers : ``celeryd``


Useful startup scripts are ``pygdv_ctl``& ``celery_ctl``. You should look at them.


Licence
================================================================
Copyright BBCF.
 
http://bbcf.epfl.ch/              
webmaster.bbcf@epfl.ch            

