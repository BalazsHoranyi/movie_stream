from django.views.generic.edit import CreateView
from .models import Rating, Movie, Follow
from .forms import FollowForm
from .ML.stream_lightfm import get_recommendations
from stream_django.enrich import Enrich
from stream_django.feed_manager import feed_manager
from movie_stream.users.models import User
from django.shortcuts import render, redirect


class RatingView(CreateView):
    model = Rating
    fields = ['movie', 'rating']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(RatingView, self).form_valid(form)


def profile_feed(request, username=None):
    """Shows user feed"""
    enricher = Enrich()
    user = User.objects.get(username=username)
    print(user)
    feed = feed_manager.get_user_feed(user.id)
    print(feed)
    activities = feed.get(limit=25)['results']
    print(activities)
    enricher.enrich_activities(activities)
    context = {
        'activities': activities
    }
    return render(request, 'pages/rating.html', context)


def follow(request):
    form = FollowForm(request.POST)
    if form.is_valid():
        follow = form.instance
        follow.user = request.user
        follow.save()
    return redirect("rating/timeline/")


def timeline(request):
    """Shows most recent updates from followed users"""
    enricher = Enrich()
    feed = feed_manager.get_news_feeds(request.user.id)['timeline']
    activities = feed.get(limit=25)['results']
    enricher.enrich_activities(activities)
    following = Follow.objects.filter(user=request.user).values_list(
        'target_id', flat=True)
    targets = User.objects.filter(id__in=following)
    context = {
        'activities': activities,
        'following': targets
    }
    return render(request, 'pages/timeline.html', context)


def discover(request):
    """Shows top recomended movies and follow recommendations."""
    movie_recs, follow_recs = get_recommendations(request.user.id)
    movie_recs = Movie.objects.filter(id__in=movie_recs).values('title')
    follow_recs = User.objects.filter(id__in=follow_recs).values('username')
    context = {
            'movie_rec': movie_recs,
            'follow_rec': follow_recs
    }
    return render(request, 'pages/discover.html', context)
