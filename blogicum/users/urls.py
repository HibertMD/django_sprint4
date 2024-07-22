from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        '<slug:username>/',
        views.UserProfileView.as_view(),
        name='profile'),
    path(
        '<slug:username>/edit_profile/',
        views.UserProfileUpdate.as_view(),
        name='edit_profile',
    )
]