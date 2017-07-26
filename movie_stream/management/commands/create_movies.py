# from django.core.management import BaseCommand
from django_tqdm import BaseCommand
import pandas as pd
import tqdm
# from django.contrib.auth import get_user_model
# User = get_user_model()
from movie_stream.models import Movie


class Command(BaseCommand):
    # Show this when the user types help
    help = "Run me to autopopulate the movie database"

    def add_arguments(self, parser):
        parser.add_argument('movies', type=str)

    def handle(self, *args, **options):
        self.stdout.write("Loading Users from disk...")
        movies_df = pd.read_csv(options['ratings'])
        movie_ids = movies_df['movieId'].unique()
        t = self.tqdm(total=len(movie_ids))
        self.stdout.write("Found %i movies " % len(movie_ids))
        self.stdout.write("Populating database...")
        for ind in movies_df.index:
            movie = Movie.objects.create(id=movies_df['movieId'][ind],
                         title=movies_df['title'][ind],
                         genres=movies_df['genres'][ind].split('|'))

            t.update(1)
