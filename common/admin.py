from django import forms
from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User

from common.models import Place, Profile, Vote, Condition

admin.site.register(Place)
admin.site.register(Profile)
admin.site.register(Vote)
admin.site.register(Condition)
