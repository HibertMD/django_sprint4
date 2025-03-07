from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from users import views

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.internal_server'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('posts/', include('blog.urls', namespace='blog')),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path(
        'auth/registration/',
        views.UserCreateView.as_view(),
        name='registration'
    ),
    path('auth/', include('django.contrib.auth.urls')),
    path('profile/', include('users.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
