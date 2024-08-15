from django.db import models


class Project(models.Model):
	title = models.CharField(max_length=100, null=False, blank=False, unique=True)
	description = models.TextField(max_length=1000, null=False, blank=False)
	employees = models.CharField(max_length=500, null=False, blank=False)


	def __str__(self):
		return self.title



