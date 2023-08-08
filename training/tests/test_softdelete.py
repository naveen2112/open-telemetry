from core.base_test import BaseTestCase
from django.utils import timezone
from hubble.models import User


class SoftDeleteTest(BaseTestCase):
    """
    This class is responsible for testing the soft delete functionalities
    """

    def test_retreive_only_delted_data(self):
        """
        Check whether the soft deleted data is alone returned
        """
        user = self.create_user()
        user.deleted_at = timezone.now()
        user.save()

        deleted_user = User.objects.trashed().first()
        self.assertEqual(user, deleted_user)

    def test_retreive_all_data(self):
        """
        Check whether the soft deleted data is also returned
        """
        user1 = self.create_user()
        user2 = self.create_user()
        user2.deleted_at = timezone.now()
        user2.save()

        users = list(User.objects.with_trashed().values_list("id", flat=True))
        self.assertEqual([user1.id, user2.id], users)

    def test_restore_deleted_data(self):
        """
        Test wheter the soft deleted data can be restored
        """
        user = self.create_user()
        user.deleted_at = timezone.now()
        user.save()

        deleted_user = User.objects.trashed().first()
        self.assertEqual(user, deleted_user)

        user.restore()
        self.assertIsNone(user.deleted_at)

        restored_user = User.objects.first()
        self.assertEqual(user, restored_user)
