from django.contrib import admin
from home.models import Category, Poll, View, Choice
# Register your models here.

admin.site.register(Category)
admin.site.register(Poll)
admin.site.register(View)
admin.site.register(Choice)