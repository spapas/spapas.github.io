Implementing a simple, Heroku-hosted REST service using Flask and mongoDB
#########################################################################

:date: 2014-06-30 15:23
:tags: flask, mongodb, heroku, python, rest
:category: flask
:slug: rest-flask-mongodb-heroku
:author: Serafeim Papastefanos
:summary: An implementation & discussion of a simple REST service with Flask that is hosted on Heroku and is using mongoDB for persistance.

.. contents::

Introduction
------------

In the following, I will describe how I used Flask_, a very nice web *microframework* for python along  with mongoDB_, the most
popular No-SQL database to implement a simple REST service that was hosted on Heroku_. This REST service would get readings from
a number of sensors from an Android device.

I chose Flask instead of Django mainly because the REST service that I needed to implement would be very simple and most of 
the Django bells and whistles (ORM, auth, admin, etc) wouldn't be needed anyway. Also, Flask is much quicker to set-up than
Django since almost everything (views, urls, etc) can be put inside one python module.

Concerning the choice of a NoSQL persistance solution (mongoDB), I wanted to have a table (or collection as it is called in the
mongoDB world) of readings from the sensor. Each reading would just have a timestamp and various other
arbitrary data depending on the type of the reading, so saving it as a JSON document in a NoSQL database is a good solution. 

Finally, all the above will be deployed to Heroku which offers some great services for deploying python code in the cloud.

Requirements
------------

I propose creating a file named ``requirements.txt`` that will host the required packages for your project, so you will be
able to setup your projects after creating a virtual environment with virtualenv_ just by running ``pip install -r requirements.txt``. 
Also, the requirements.txt is required for deploying python to Heroku.

So, for my case, the contents of requirements.txt are the following:

.. code::

  Flask==0.10.1
  Flask-PyMongo==0.3.0
  Flask-RESTful==0.2.12
  Jinja2==2.7.3
  MarkupSafe==0.23
  Werkzeug==0.9.6
  aniso8601==0.82
  gunicorn==19.0.0
  itsdangerous==0.24
  pymongo==2.7.1
  pytz==2014.4
  six==1.7.2
  
* Flask-PyMongo is a simple wrapper for Flask around pymongo which is the python mongoDB driver. 
* Flask-RESTful is a simple library for creating REST APIs - it needs aniso8601 and pytz. 
* Jinja2 is the template library for Flask (we won't use it but it is required by Flask installation) - it needs MarkupSafe.
* Werkzeug is a WSGI utility library - required by Flask
* gunicorn is a WSGI HTTP server - needed for deployment to Heroku
* itsdangerous is used to sign data for usage in untrusted environments
* six is the python 2/3 compatibility layer

Implementing the REST service
-----------------------------

Instead of using just one single file for our Flask web application, we will create a python module to contain it and a 
file named ``runserver.py`` that will start a local development server to test it: 

So, in the same folder as the ``requirements.txt`` create a folder named ``flask_rest_service`` and in there put
two files: ``__init__.py`` and ``resources.py``. 

The ``__init__.py`` initializes our Flask application, our mongoDB connection and our Flask-RESTful api:

.. code::

    import os
    from flask import Flask
    from flask.ext import restful
    from flask.ext.pymongo import PyMongo
    from flask import make_response
    from bson.json_util import dumps

    MONGO_URL = os.environ.get('MONGO_URL')
    if not MONGO_URL:
        MONGO_URL = "mongodb://localhost:27017/rest";

    app = Flask(__name__)
    
    app.config['MONGO_URI'] = MONGO_URL
    mongo = PyMongo(app)

    def output_json(obj, code, headers=None):
        resp = make_response(dumps(obj), code)
        resp.headers.extend(headers or {})
        return resp

    DEFAULT_REPRESENTATIONS = {'application/json': output_json}
    api = restful.Api(app)
    api.representations = DEFAULT_REPRESENTATIONS

    import flask_rest_service.resources

So what happens here? After the imports, we check if we have a MONGO_URL environment variable. This is
how we set options in Heroku. If such option does not exist in the environment then we are in our 
development environment so we set it to the localhost (we must have a running mongoDB installation in
our dev environment).

In the next lines, we initialize our Flask application and our mongoDB connection (pymongo 
uses a ``MONGO_URI`` configuration option to know the database URI).

The ``output_json`` is used to dump the BSON encoded mongoDB objects to JSON and was borrowed from
`alienretro's blog`_ -- we initialize our restful REST API with this function. 

Finally, we import the ``resources.py`` module which actually defines our REST resources.

.. code::

    import json
    from flask import request, abort
    from flask.ext import restful
    from flask.ext.restful import reqparse
    from flask_rest_service import app, api, mongo
    from bson.objectid import ObjectId

    class ReadingList(restful.Resource):
        def __init__(self, *args, **kwargs):
            self.parser = reqparse.RequestParser()
            self.parser.add_argument('reading', type=str)
            super(ReadingList, self).__init__()

        def get(self):
            return  [x for x in mongo.db.readings.find()]

        def post(self):
            args = self.parser.parse_args()
            if not args['reading']:
                abort(400)
            
            jo = json.loads(args['reading'])
            reading_id =  mongo.db.readings.insert(jo)
            return mongo.db.readings.find_one({"_id": reading_id})
            

    class Reading(restful.Resource):
        def get(self, reading_id):
            return mongo.db.readings.find_one_or_404({"_id": reading_id})
            
        def delete(self, reading_id):
            mongo.db.readings.find_one_or_404({"_id": reading_id})
            mongo.db.readings.remove({"_id": reading_id})
            return '', 204
            

    class Root(restful.Resource):
        def get(self):
            return {
                'status': 'OK',
                'mongo': str(mongo.db),
            }

    api.add_resource(Root, '/')
    api.add_resource(ReadingList, '/readings/')
    api.add_resource(Reading, '/readings/<ObjectId:reading_id>')

Here we define three ``Resource`` classes and add them to our previously defined ``api``: ``Root``, ``Reading`` and ``ReadingList``.

``Root`` just returns a dictionary with an OK status and some info on our mongodb connection. 

``Reading`` has gets an ObjectId 
(which is the mongodb primary key) as a parameter and depending on the HTTP operation, it returns the reading with that
id when receiving an ``HTTP GET`` and deletes the reading with that id when receiving an ``HTTP DELETE``.

``ReadingList`` will return all readings when receiving an ``HTTP GET`` and will create a new reading when
receiving an ``HTTP POST`` The ``post`` function uses the parser defined in ``__init__`` which requires
a ``reading`` parameter with the actual reading to be inserted.


Testing it locally
------------------

In order to run the development server, you will need to install and start mongodb locally which is beyond the scope of this post. After that
create a file named ``runserver.py`` in the same folder as with the ``requirements.txt``
and the ``flask_rest_service`` folder. The contents of this file should be:

.. code::

    from flask_rest_service import app
    app.run(debug=True)

When you run this file with ``python runserver.py`` you should be able top visit your rest service at http://localhost:5000 and get
an "OK" status. 
    

Deploying to Heroku
-------------------

To deploy to Heroku, you must create a ``Procfile`` that contains the workers of your application. In our case, the
``Procfile`` should contain the following:

.. code::

  web: gunicorn flask_rest_service:app

Also, you should add a .gitignore file with the following:

.. code::

    *.pyc

Finally, to deploy your application to Heroku you can follow the instructions here: https://devcenter.heroku.com/articles/getting-started-with-python: 

* Initialize a git repository and commit everything:

.. code:: 

  git init
  git add .
  git commit -m    
  
* Create a new Heroku application (after logging in to heroku with ``heroku login``) and set the MONGO_URL environment variable (of course you have to obtain ths MONGO_URL variable for your heroku envirotnment by adding a mongoDB database):

.. code::
   
   heroku create 
   heroku config:set MONGO_URL=mongodb://user:pass@mongoprovider.com:27409/rest
   
* And finally push your master branch to the heroku remote repository:

.. code::
  
   git push heroku master

If everything went ok you should be able to start a worker for your application, check that the worker is running, and finally visit it:

.. code::

     heroku ps:scale web=1
     heroku ps
     heroku open

If everything was ok you should see an status-OK JSON !   
     
    
.. _Flask: http://flask.pocoo.org/
.. _mongoDB: http://www.mongodb.org/
.. _Heroku: https://dashboard.heroku.com/apps
.. _virtualenv: http://virtualenv.readthedocs.org/en/latest/
.. _`alienretro's blog`: http://blog.alienretro.com/using-mongodb-with-flask-restful/