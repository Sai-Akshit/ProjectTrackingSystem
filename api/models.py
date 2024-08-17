from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import URLValidator


class Project(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.TextField(max_length=1000, null=False, blank=False)
    employees = models.CharField(max_length=500, null=False, blank=False)

    def __str__(self):
        return self.title


class Scrum(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=1000)
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created = models.DateField()
    modified = models.DateField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Scrum, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


"""Choices for status"""
status_choices = (
    ("not_started", "Not Started"),
    ("in_progress", "In Progress"),
    ("under_review", "Under Review"),
    ("completed", "Completed"),
)


class Task(models.Model):
    scrum = models.ForeignKey(Scrum, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=1000)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_assigned_to",
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_assigned_by",
    )
    end_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=status_choices, default="not_started"
    )
    link = models.URLField(
        max_length=200, null=True, blank=True, validators=[URLValidator()]
    )
    created = models.DateField(null=True, blank=True)
    modified = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Task, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
