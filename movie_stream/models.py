from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete, post_save
from stream_django.activity import Activity
from stream_django.feed_manager import feed_manager
from django.contrib.postgres.fields import ArrayField
from movie_stream.users.models import User
from stream_django.activity import Activity
from stream_django.feed_manager import feed_manager
from django.db.models import signals
import datetime
import time
# from movie_stream.taskapp.tasks import picklemodel



class Movie(models.Model):
    """Movie model to store Names and Genres."""

    id = models.IntegerField(primary_key=True)
    title = models.TextField()
    genres = ArrayField(ArrayField(
        models.CharField(max_length=20)))


class Rating(Activity, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField()
    timestamp = models.DateTimeField(default=datetime.datetime.today)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')

    @property
    def print_self(self):
        print(self.text)

    @property
    def activity_object_attr(self):
        return self


class LightFMModel(models.Model):
    pickle_model = models.BinaryField()
    created_at = models.DateTimeField(auto_now_add=True)





class Follow(models.Model):
    user = models.ForeignKey(User, related_name='friends')
    target = models.ForeignKey(User, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'target')


def unfollow_feed(sender, instance, **kwargs):
    feed_manager.unfollow_user(instance.user_id, instance.target_id)


def follow_feed(sender, instance, created, **kwargs):
    if created:
        feed_manager.follow_user(instance.user_id, instance.target_id)


signals.post_delete.connect(unfollow_feed, sender=Follow)
signals.post_save.connect(follow_feed, sender=Follow)
