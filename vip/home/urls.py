"""easyleave URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. polld an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.urls import path, include
# from . import views
# app_name= 'home'
# urlpatterns = [
#     path('', views.home, name='home'),
# ]

from django.urls import path, reverse_lazy
from . import views

app_name='home'
urlpatterns = [
    path('about/', views.AboutView, name='about'),
    path('contact/', views.ContactView, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('search/', views.SearchView, name='search_user'),
    path('user/<str:viewusername>', views.UserDetail, name='user_detail'),
    path('follow/<str:viewusername>', views.FollowView, name='follow'),
    path('unfollow/<str:viewusername>', views.UnfollowView, name='unfollow'),
    path('followers/<str:username>', views.FollowersView, name='followers'),
    path('followings/<str:username>', views.FollowingsView, name='followings'),
    # path('user/<str:username>', views.UserPostListView.as_view(), name='user-posts'),
    path('', views.PollListView.as_view()),
    path('polls/', views.PollListView.as_view(), name='all'),
    path('poll/<int:pk>', views.PollDetailView.as_view(), name='poll_detail'),
    path('issue/<int:pk>', views.IssueDetailView.as_view(), name='issue_detail'),
    path('poll/<int:pk>/results', views.PollResultView.as_view(), name='poll_result'),
    path('poll/<int:poll_id>/vote', views.vote, name='vote'),
    path('poll/create',
        views.PollCreateView.as_view(success_url=reverse_lazy('home:all')), name='poll_create'),
    path('issue/create',
        views.IssueCreateView.as_view(success_url=reverse_lazy('home:all')), name='issue_create'),
    path('poll/<int:pk>/update',
        views.PollUpdateView.as_view(success_url=reverse_lazy('home:all')), name='poll_update'),
    path('poll/<int:pk>/delete',
        views.PollDeleteView.as_view(success_url=reverse_lazy('home:all')), name='poll_delete'),
    path('issue/<int:pk>/update',
        views.IssueUpdateView.as_view(success_url=reverse_lazy('home:all')), name='issue_update'),
    path('issue/<int:pk>/delete',
        views.IssueDeleteView.as_view(success_url=reverse_lazy('home:all')), name='issue_delete'),
    path('poll_picture/<int:pk>', views.stream_file, name='poll_picture'),
    path('poll/<int:pk>/comment',
        views.CommentCreateView.as_view(), name='poll_comment_create'),
    path('comment/<int:pk>/delete',
        views.CommentDeleteView.as_view(success_url=reverse_lazy('polls')), name='poll_comment_delete'),
    
    path('issue_picture/<int:pk>', views.istream_file, name='issue_picture'),
    path('issue/<int:pk>/comment',
        views.IssueCommentCreateView.as_view(), name='issue_comment_create'),
    path('issuecomment/<int:pk>/delete',
        views.IssueCommentDeleteView.as_view(success_url=reverse_lazy('polls')), name='issue_comment_delete'),

    path('poll/<int:pk>/favorite',
    views.AddFavoriteView.as_view(), name='poll_favorite'),
    path('poll/<int:pk>/unfavorite',
    views.DeleteFavoriteView.as_view(), name='poll_unfavorite'),
]

