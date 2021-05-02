from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.favorites, name='favorites'),
    # Used to remove a product (identified by favorite_id) from favorites
    url(r'^del_fav/(?P<favorite_id>[0-9]+)/$',
        views.remove_from_fav, name='del_fav'),
    url(r'^search/$', views.search_in_fav, name='search_fav'),
]
