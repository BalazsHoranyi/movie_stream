# from django.core.management import BaseCommand
from django_tqdm import BaseCommand
import pandas as pd
from movie_stream.models import Rating, Movie
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):
    # Show this when the user types help
    help = ("Read in ratings.csv"
            " to populate user database. This may take a bit depending"
            " on your computer speed and internet connection as every movie"
            " rating is creating an event at getstream.io. It is however"
            " resumable")

    def add_arguments(self, parser):
        parser.add_argument('ratings', type=str)

    def handle(self, *args, **options):
        self.stdout.write("Loading Users from disk...")
        ratings_df = pd.read_csv(options['ratings'])
        user_ids = ratings_df['userId'].unique()
        t = self.tqdm(total=len(user_ids))
        self.stdout.write("Found %i users " % len(user_ids))
        self.stdout.write("Populating database...")
        for user_id in user_ids:
            # try catch statement makes this resumable
            try:
                user = User.objects.create_user(
                    username='user_%i' % user_id,
                    email='user_%i@example.com' % user_id,
                    password='getstreamio')
                user_ratings = ratings_df[ratings_df['userId'] == user_id]

                # Can't use bulk create with stream api to register events
                # Rating.objects.bulk_create(
                #     [Rating(user=user,
                #             movie=Movie.objects.get(pk=user_ratings['movieId'][ind]),
                #             rating=user_ratings['rating'][ind],
                #             timestamp=pd.to_datetime(
                #                 user_ratings['timestamp'][ind], unit='s'))
                #      for ind in user_ratings.index])

                for ind in user_ratings.index:
                    movie = Movie.objects.get(pk=user_ratings['movieId'][ind])
                    Rating.objects.create(
                        user=user,
                        movie=movie,
                        rating=user_ratings['rating'][ind],
                        timestamp=pd.to_datetime(
                            user_ratings['timestamp'][ind], unit='s'))

                t.update(1)
            except Exception as e:
                # Looks like we already created that user,
                # or there was an error pushing to to getstream.io
                t.update(1)
