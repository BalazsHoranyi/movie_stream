from django.forms import ModelForm
from movie_stream.models import Follow


class FollowForm(ModelForm):

    class Meta:
        exclude = set()
        model = Follow
