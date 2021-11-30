from django.urls import include, path
from rest_framework import routers

from api.views import (AuthorViewSet, BookViewSet, FollowViewSet,
                       LanguageViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register('authors', AuthorViewSet, basename='authors')
router.register('books', BookViewSet, basename='books')
router.register('follows', FollowViewSet, basename='follows')
router.register('languages', LanguageViewSet, basename='languages')

urlpatterns = [
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
    path('v1/', include(router.urls)),
]
