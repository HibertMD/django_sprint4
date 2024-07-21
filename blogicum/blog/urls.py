from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(),
         name='index'
         ),
    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'
         ),
    path('create/',
         views.PostCreateView.as_view(),
         name='create_post'
         ),
    path('<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'
         ),
    path('<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'
         ),
    path('category/<slug:category_slug>/',
         views.PostListView.as_view(),
         name='category_posts'
         )
]
