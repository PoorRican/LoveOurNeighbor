from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Activity(models.Model):
    user = models.ForeignKey('people.User', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    # TODO: OneToOne field for comments

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, obj, user):
        cls.objects.create(user=user, content_object=obj)

    class Meta:
        abstract = True


class Like(Activity):
    @classmethod
    def liked(cls, obj, user) -> bool:
        return obj in obj.__class__.objects.filter(likes__user=user)

    @classmethod
    def unlike(cls, obj, user):
        ct = ContentType.objects.get_for_model(obj)
        cls.objects.filter(content_type=ct, object_id=obj.pk, user=user).delete()

    @classmethod
    def do(cls, obj, user) -> bool:
        """
        Check and perform the 'liking' or 'un-liking'...

        See Also
        --------
        `Activity.__call__`
        """
        if cls.liked(obj, user):
            cls.unlike(obj, user)
            return False
        else:
            cls.create(obj, user)
            return True


class View(Activity):
    pass


class Comment(Activity):
    content = models.TextField()

    @classmethod
    def create(cls, obj, user, comment):
        cls.objects.create(user=user, content_object=obj, comment=comment)
