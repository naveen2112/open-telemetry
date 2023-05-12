from django.db import models
import datetime

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def with_trashed(self):
        return super().get_queryset()

    def trashed(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteWithBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    objects = SoftDeleteManager()
    

    class Meta:
        abstract = True

    
    def delete(self, *args, **kwargs):
        """
        This function sets the "deleted_at" attribute to the current datetime and saves the object.
        """
        self.deleted_at = datetime.datetime.now()
        self.save()


    def restore(self):
        """
        This function restores a deleted object by setting its "deleted_at" attribute to None and saving it.
        """
        self.deleted_at = None
        self.save()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        abstract = True

