from django.contrib.auth.models import User
from django.contrib.postgres import fields as pgfields
from django.db import models
from django.utils import timezone


class Extension(models.Model):
    name = models.CharField(max_length=256)
    gecko_id = models.CharField(max_length=256, unique=True)
    created = models.DateTimeField(default=timezone.now)

    @property
    def authors(self):
        return self.releases.values_list("author", flat=True).order_by("author")


class Release(models.Model):
    extension = models.ForeignKey(Extension, related_name="releases", on_delete=models.CASCADE)
    private = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    version = models.CharField(max_length=32)
    author = models.CharField(max_length=128)
    signing_key = models.CharField(max_length=32, null=True)
    xpi_url = models.URLField()
    notes = models.TextField()
    manifest = pgfields.JSONField()

    @property
    def is_signed(self):
        return self.signing_key is not None

    @property
    def is_deprecated(self):
        return self.deprecation is not None


class Deprecation(models.Model):
    release = models.OneToOneField(Release, related_name="deprecation", on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    creator = models.ForeignKey(
        User, null=True, related_name="deprecations", on_delete=models.SET_NULL
    )
    reason = models.TextField()


class Signoff(models.Model):
    release = models.ForeignKey(Release, related_name="signoffs", on_delete=models.CASCADE)
    role = models.CharField(max_length=32)
    user = models.CharField(max_length=64)
