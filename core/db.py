"""
Module containing custom model fields, managers, and abstract base
models for the project
"""
import datetime

from django.db import models


class DateTimeWithoutTZField(models.DateTimeField):
    """
    A custom DateTimeField that selects the appropriate database-specific
    column type based on the database engine.

    Overrides the `db_type` method to return the appropriate column type for
    PostgreSQL, MySQL, and SQLite.For other database engines, it falls back
    to the default behavior of the parent class.
    """

    def db_type(self, connection):
        # Use the appropriate database-specific column type
        if connection.settings_dict["ENGINE"] == "django.db.backends.postgresql":
            return "timestamp without time zone"
        if connection.settings_dict["ENGINE"] == "django.db.backends.mysql":
            return "datetime"
        if connection.settings_dict["ENGINE"] == "django.db.backends.sqlite3":
            return "datetime"
        return super().db_type(connection)


class BaseModel(models.Model):
    """
    Abstract base model class that provides 'created_at' and 'updated_at'
    fields
    """

    created_at = DateTimeWithoutTZField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        abstract = True


class SoftDeleteManager(models.Manager):
    """
    Manager class for soft-deletable models that filters out
    deleted instances.Provides additional methods for querying deleted and
    non-deleted instances.
    """

    def get_queryset(self):
        """
        Returns a queryset that filters out deleted instances
        """
        return super().get_queryset().filter(deleted_at__isnull=True)

    def with_trashed(self):
        """
        Returns a queryset including all instances, including deleted ones
        """
        return super().get_queryset()

    def trashed(self):
        """
        Returns a queryset that only includes deleted instances
        """
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteWithBaseModel(BaseModel):
    """
    Abstract base model class that adds soft-delete functionality to a model.
    """

    created_at = DateTimeWithoutTZField(auto_now_add=True)
    updated_at = DateTimeWithoutTZField(auto_now=True)
    deleted_at = DateTimeWithoutTZField(null=True)

    objects = SoftDeleteManager()

    class Meta:
        """
        Meta class for defining class behavior and properties.
        """

        abstract = True

    # It is used to ommit 'unused-argument'.The function has unused arguments
    # pylint: disable=unused-argument
    def delete(self, *args, **kwargs):
        """
        This function sets the "deleted_at" attribute to the current datetime
        and saves the object.
        """
        self.deleted_at = datetime.datetime.now()
        self.save()

    def restore(self):
        """
        This function reStore a deleted object by setting its "deleted_at"
        attribute to None and saving it.
        """
        self.deleted_at = None
        self.save()

    @classmethod
    def bulk_delete(cls, filters):
        """
        Performs a bulk delete operation on objects matching the
        specified filters
        """
        cls.objects.filter(**filters).update(deleted_at=datetime.datetime.now())
