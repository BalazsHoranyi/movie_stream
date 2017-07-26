movie_stream
============

Example recommendation app using getstream.io

Built with Cookiecutter Django, getstream.io, LightFM, and Celery


About
----------

This app is the start to a movie recommendation social network.
It allows users to rate movies, follow other users, see what other users have rated movies,
and it also provides recommendations  of other movies to watch and other movie watchers to follow.

It utilizes the LightFM library to provide recommendations of movies using matrix factorization techniques and takes advantage of the generated user feature vectors to provide follow recommendations.
Follow recommendations are based on to cosine similar between different user feature vectors.
Assuming that people want to follow other people who have similar taste to them.

The LightFM model is retrained anytime a new user or rating is created and then stored for later predictions.


Basic Commands
--------------

Setting Up Your Database
^^^^^^^^^^^^^^^^^^^^^^^^


* Set up a postgres database on your localhost with the following.

  * name: *stream_db*

  * username: *stream_user*

  * password: *stream_user*

Or feel free to change the config file to utilize your settings. However I do make use of the array field in postgres.
Then run your standard commands to set up your database

.. code-block:: bash

    python manage.py makemigrations
    python manage.py migrate



* This app comes with some convenience functions to auto-populate a database using MovieLens data which can be found at <https://grouplens.org/datasets/movielens/latest/>
I recommend downloading the *ml-latest-small.zip* for testing.
* To add all movies from you may run::

  $ python manage.py create_movies path/to/movies.csv

  Where *path/to/movies.csv* is the path to the ratings.csv file you just downloaded.

* To add all users and user ratings you may run::

  $ python manage.py create_users path/to/ratings.csv

  However I would strongly recommended commenting out the post save hooks above *calculate_model* under *movie_stream/taskapp/tasks.py*
  Otherwise it will try and kick off a whole bunch of machine learning tasks. Just make sure to uncomment it after you run the command.
  This admin command may take a bit depending on internet speed, as it is also integrating with a stream api.
  It is however resumable and you don't have to wait for it to finish to move on.

Celery
^^^^^^^

This app comes with Celery and is utilized it to run LightFM model generation in the background.

The default configuration for the broker is utilizing the following broker url: *'amqp://guest:guest@localhost:5672'*
Which is a rabbitmq broker running on local host. You may however use your favorite broker as long as your change the broker url under *setting/base.py*



To run a celery worker:

.. code-block:: bash

  cd movie_stream
  celery -A movie_stream.taskapp worker -l info -E

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.



Interesting Links
-------------------

Assuming your running a django development server on <http://localhost:8000>

You may either create a new user or login under user_xx with password 'getstreamio'
where xx is any number between 1 and 670 (Assuming you used the *ml-latest-small ratings.csv file to load the database)

A list of movies a user has rated.
<http://localhost:8000/ratings/feed/user_1>

A list of people who you follow and the most recent movies they've rated.
<http://localhost:8000/ratings/timeline/>

A list of recommended movies to watch and people to follow.
<http://localhost:8000/ratings/discover/>


How to rate and follow
-------------------------
Theres is no front end interface to rate movies and follow users however it can be done programmatically.

.. code-block:: bash

    cd movie_stream
    python manage.py shell

To have users follow each other:

.. code-block:: python

    from movie_stream.models import Follow
    user = User.objects.get(username='user_1')
    target = User.objects.get(username='user_14')
    Follow.objects.create(user = first,
                          target = other)

To rate a movie:

.. code-block:: python

    from movie_stream.models import Movie
    from movie_stream.users.models import User

    user = User.objects.all().first()
    movie = Movie.objects.get(pk=1)
    Rating.objects.create(user=user,
                        movie=movie,
                        rating=4.5)


TODO and future recommendations
----------------------------------

* store n_features and n_items for LightFm in the database so we don't have to load the whole thing into memory every time.

* Don't run ML model every time a database transaction is initiated. Run every X minutes depending on time constraints.

* Create API hooks for ML models to utilize favorite front end.

* Utilize already followed users to better recommend things.
