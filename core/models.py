# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from django.conf import settings


class Candidates(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_url = models.TextField(blank=True, null=True)
    full_name = models.CharField(max_length=255)
    head_line = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    education = models.JSONField(blank=True, null=True)
    experience = models.JSONField(blank=True, null=True)
    skills = models.JSONField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=False, null=False)

    class Meta:
        db_table = "candidates"
