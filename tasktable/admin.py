from django.contrib import admin
from .models import Task, Project, Status, File, Notification

# Register your models here.
admin.site.register(Task)
admin.site.register(Project)
admin.site.register(Status)
admin.site.register(File)
admin.site.register(Notification)
