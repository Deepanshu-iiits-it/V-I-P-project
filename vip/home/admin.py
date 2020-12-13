from django.contrib import admin
from home.models import Category, Poll, View, Choice, Profile, Fav, Follow, Comment, IssueComment
# Register your models here.

admin.site.register(Category)
admin.site.register(Poll)
admin.site.register(View)
admin.site.register(Choice)
admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(IssueComment)