# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, app
import pandas as pd
import pickle
from scipy.sparse import coo_matrix
from lightfm import LightFM
from movie_stream.models import Rating, Movie, LightFMModel
from django.dispatch import receiver
from django.db.models.signals import post_save
from celery import task

@task()
def picklemodel():

    ratings_df = pd.DataFrame.from_records(
        Rating.objects.all().values('movie_id', 'rating', 'user_id'))
    movies_df = pd.DataFrame.from_records(
        Movie.objects.all().values('id', 'title'))
    ratings_df = ratings_df.pivot(
        index='user_id', columns='movie_id', values='rating')
    train_sparse = coo_matrix(ratings_df)

    model = LightFM(no_components=30,loss='warp')
    model.fit(train_sparse, epochs=1, verbose=True)
    print("Finished fitting model")
    # Pickle model and dump into database for later.
    pickle_model = pickle.dumps(model)
    print("Finished pickle")
    try:
        LightFMModel.objects.create(pickle_model=pickle_model)
    except Exception as e:
        print(e[:200])
    return "Success!"


@receiver(post_save, sender=Rating)
def calculate_model(sender, instance, **kwargs):
    picklemodel.delay()


@task()
def add(x, y):
    print("adding")
    return x + y
