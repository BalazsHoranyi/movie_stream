import pandas as pd
from scipy.sparse import coo_matrix
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from movie_stream.models import Rating, Movie, LightFMModel
import pickle
from movie_stream.users.models import User


def get_recommendations(userid):
    """Get movie and follow recommendations for a user.

    Args:
        userid (int): id of a user in database
    """
    ratings_df = pd.DataFrame.from_records(
        Rating.objects.all().values('movie_id', 'rating', 'user_id'))
    movies_df = pd.DataFrame.from_records(
        Movie.objects.all().values('id', 'title'))
    ratings_df = ratings_df.pivot(
        index='user_id', columns='movie_id', values='rating')
    train_sparse = coo_matrix(ratings_df)

    model = pickle.loads(
        LightFMModel.objects.all().last().pickle_model)  # get last model
    # should really just store n_users and n_tems in database
    # so we don't have to load the whold database everytime
    n_users, n_items = train_sparse.shape

    user_row = ratings_df.index.tolist().index(userid)
    # This will fail unless model has run at least once for user
    scores = model.predict(user_row, np.arange(n_items))
    # rank them in order of most liked to least
    top_items = movies_df['id'].values[np.argsort(-scores)]

    # Now we can use the feature vectors of each user to find who
    # is the most similar to them. (Likes the same type of movies)
    similarities = cosine_similarity(model.user_embeddings)
    ind = np.argpartition(similarities[user_row], -6)[-6:]

    to_follow_ids = ratings_df.index[ind].tolist()
    # don't want to recomend to follow user self
    to_follow_ids.remove(userid)
    return top_items[:10], to_follow_ids
