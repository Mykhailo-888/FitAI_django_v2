# fitness/admin.py

from django.contrib import admin
from .models import UserData  # тільки UserData

admin.site.register(UserData)