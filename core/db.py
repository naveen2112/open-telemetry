from django.db import models
import datetime

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        return super().get_queryset()

    def deleted(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = SoftDeleteManager()

    class Meta:
        abstract = True


    def delete(self, *args, **kwargs):
        self.deleted_at = datetime.datetime.now()
        self.save()


    def restore(self):
        self.deleted_at = None
        self.save()

