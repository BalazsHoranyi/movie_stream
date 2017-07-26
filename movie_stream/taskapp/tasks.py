# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import pandas as pd
import pickle
from scipy.sparse import coo_matrix
from lightfm import LightFM
from movie_stream.models import Rating, Movie, LightFMModel
from django.dispatch import receiver
from django.db.models.signals import post_save
from movie_stream.users.models import User


@shared_task
def picklemodel():
    """Use user rating to run LightFM Model."""
    ratings_df = pd.DataFrame.from_records(
        Rating.objects.all().values('movie_id', 'rating', 'user_id'))
    movies_df = pd.DataFrame.from_records(
        Movie.objects.all().values('id', 'title'))
    ratings_df = ratings_df.pivot(
        index='user_id', columns='movie_id', values='rating')
    train_sparse = coo_matrix(ratings_df)

    model = LightFM(no_components=30, loss='warp')
    # you can play around with number of epochs.
    # trade of is accuracy vs speed of traning.
    model.fit(train_sparse, epochs=30, verbose=True)
    print("Finished fitting model")
    # Pickle model and dump into database for later.
    pickle_model = pickle.dumps(model)
    print(len(pickle_model))
    print("Finished pickle")
    try:
        print(type(pickle_model))
        LightFMModel.objects.create(pickle_model=pickle_model)
    except Exception as e:
        print(str(e)[:100])
    return "Success!"


# For a production app we would need to be smarter about when to update
# the ML model. Running every time something changes is a lot, and could
# run behind based on how long it takes to run and how many updates there are
@receiver(post_save, sender=Rating)
@receiver(post_save, sender=User)
def calculate_model(sender, instance, **kwargs):
    """Anytime a user or rating is updated, update lightFM Model.
        Make sure to comment this out when running 'manage.py create_users'
        or it's going to create a LOT of tasks.
    """
    # TODO make sure transaction was commited before trying to update model
    picklemodel.delay()


@shared_task
def add(x, y):
    """Dummy task to test celery."""
    print("adding")
    return x + y
