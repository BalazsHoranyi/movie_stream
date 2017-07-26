from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from movie_stream import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^create/', login_required(views.RatingView.as_view()), name='create_rating'),
    url(r'^feed/(?P<username>(.+))', login_required(views.profile_feed), name='view_ratings'),
    url(r'^timeline/', login_required(views.timeline), name='timeline'),
    url(r'^follow/', login_required(views.follow), name='follow'),
    url(r'^discover/', login_required(views.discover), name='discover'),

]
