from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Subject)
admin.site.register(Test)
admin.site.register(Image)
admin.site.register(BotUser)
admin.site.register(MainPostForBot)
admin.site.register(Course)
admin.site.register(AvailableCourse)
admin.site.register(TgGroup)
admin.site.register(SubjectBranch)
admin.site.register(ForwardMessage)
