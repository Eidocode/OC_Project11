from django.conf.urls import url

from . import views


urlpatterns = [
    # Used when selecting a product
    url(r'^(?P<product_id>[0-9]+)/$', views.result, name='result'),
    url(r'^(?P<product_id>[0-9]+)/detail/$', views.detail, name='detail'),
    url(r'^search/$', views.search, name='search'),

    # Used when adding a product to the user's favorites
    url(r'^add_fav/(?P<product_id>[0-9]+)/$', views.add_fav, name='add_fav'),
]
