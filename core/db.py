import datetime

from django.db import models


class DateTimeWithoutTZField(models.DateTimeField):
    def db_type(self, connection):
        # Use the appropriate database-specific column type
        if (
            connection.settings_dict["ENGINE"]
            == "django.db.backends.postgresql"
        ):
            return "timestamp without time zone"
        elif (
            connection.settings_dict["ENGINE"]
            == "django.db.backends.mysql"
        ):
            return "datetime"
        elif (
            connection.settings_dict["ENGINE"]
            == "django.db.backends.sqlite3"
        ):
            return "datetime"
        else:
            return super().db_type(connection)


class BaseModel(models.Model):
    created_at = DateTimeWithoutTZField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def with_trashed(self):
        return super().get_queryset()

    def trashed(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteWithBaseModel(BaseModel):
    created_at = DateTimeWithoutTZField(auto_now_add=True)
    updated_at = DateTimeWithoutTZField(auto_now=True)
    deleted_at = DateTimeWithoutTZField(null=True)

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

    @classmethod
    def bulk_delete(cls, filters):
        cls.objects.filter(**filters).update(
            deleted_at=datetime.datetime.now()
        )
