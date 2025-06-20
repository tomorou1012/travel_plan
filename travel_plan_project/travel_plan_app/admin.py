from django.contrib import admin

# Register your models here.
from .models import Member, Post, Prefecture, Weather, Day

admin.site.register(Member)
admin.site.register(Post)
admin.site.register(Prefecture)
admin.site.register(Weather)
admin.site.register(Day)