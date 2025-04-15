from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import custom_logout_view
from .apiview import *

urlpatterns = [
    # Frontend URLs
    path('', views.channel_list, name='channel_list'),
    path('add/', views.add_channel, name='add_channel'),
    path('channel/<int:channel_id>/', views.media_list, name='media_list'),
    path('audio-list/', views.audio_list, name='audio_list'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='downloader/login.html'), name='login'),
    path('logout/', custom_logout_view, name='custom-logout'),
    
    # API URLs
    path('api/channels/', YouTubeChannelCreateAPIView.as_view(), name='channel_create'),
    path('api/media-urls/', MediaURLListCreateAPIView.as_view(), name='media_url_list_create'),
    path('api/media-urls/<int:pk>/', MediaURLDetailAPIView.as_view(), name='media_url_detail'),
    path('api/downloaded-audio/', DownloadedAudioListAPIView.as_view(), name='downloaded_audio_list'),
    path('api/downloaded-audio/<int:pk>/', DownloadedAudioDetailAPIView.as_view(), name='downloaded_audio_detail'),
]