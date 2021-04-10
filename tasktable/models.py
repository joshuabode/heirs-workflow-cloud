from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timezone
from django.utils import timezone

# Create your models here. Reload

IMPORTANCE = (
    ('High', 'High'),
    ('Medium', 'Medium'),
    ('Low', 'Low'),
)

STATE = (
    ('On Track', 'On Track'),
    ('Stuck', 'Stuck'),
    ('Ready for Approval', 'Ready for Approval'),
    ('Behind Schedule', 'Behind Schedule'),
)

FILE_TYPES = (
    ('critical_files', 'Critical'),
    ('references', 'Reference'),
    ('submissions', 'Submission'),
)


def task_references_path(instance, filename):
    return '{0}/{1}/references/{2}'.format(instance.project, instance.name, filename)


def task_submits_path(instance, filename):
    return '{0}/{1}/submits/{2}'.format(instance.project, instance.name, filename)


def project_file_space(instance, filename):
    return '{0}/{1}/{2}'.format(instance.project, instance.type, instance.name)


def get_time_until_due(instance):
    delta = instance.due_date - datetime.now(timezone.utc)
    if delta.days > 0:
        return '{0} days'.format(delta.days)
    elif delta.days == 0:
        return 'today'
    elif delta.days == -1:
        return 'yesterday'
    elif delta.days == 1:
        return 'tomorrow'
    else:
        return '{0} days ago'.format(abs(delta.days))


class Notification(models.Model):
    title = models.CharField(max_length=50, unique=True)
    recipients = models.ManyToManyField(User)
    description = models.CharField(max_length=150)
    date_time_created = models.DateTimeField(
        default=timezone.now, blank=True)
    time_ago = models.CharField(max_length=20, null=True, blank=True)
    link_url = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.title


class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    members = models.ManyToManyField(User)
    founding_date = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return self.name


class Status(models.Model):
    class Meta:
        verbose_name_plural = "Statuses"
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    status = models.CharField(max_length=300)

    def __str__(self):
        return str(self.user.first_name) + ' ' + str(self.user.last_name) + ': ' + self.status


class File(models.Model):
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(choices=FILE_TYPES, max_length=14)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to=project_file_space)
    upload_date = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return self.name + ' ' + '(' + self.type + ')'


class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=260)
    assigned_date = models.DateTimeField(
        'Date Assigned', default=timezone.now, blank=True)
    due_date = models.DateTimeField('Date Due')
    importance = models.CharField(choices=IMPORTANCE, max_length=6)
    assignees = models.ManyToManyField(User, related_name='assignees')
    manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='manager')
    references = models.ManyToManyField(
        File, blank=True, related_name='references')
    submissions = models.ManyToManyField(File, blank=True)
    due_in = get_time_until_due
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True)
    state = models.CharField(
        choices=STATE, max_length=18, blank=True
    )
    status = models.ManyToManyField(
        Status, blank=True)
    approved = models.BooleanField(default=False)
    pre_approved = models.BooleanField(default=False)
    feedback = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name
