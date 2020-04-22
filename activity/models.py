from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Activity(models.Model):
    """
    An abstract base model for storing user activity with other objects.

    Specific activities are to be subclassed as to have schema separation, more attributes,
    and class methods.

    Methods
    -------
    user: people.User (optional)
        User who initiated the action.

        If an activity is blank, it was initiated by an AnonymousUser. The only subclass that this
        applies to is `View`.

    content_object: GenericForeignKey
        An abstract object with which this instance relates to. Non-specified type allows
        broader relations.

        E.g:
            - User may "like" a Post, Campaign, Church, Ministry, etc
            - User can "message" a Church, Ministry, other User, etc
            - User can "view" a Post, Campaign, Church, Ministry, other User, etc
            - User can "comment" on a Post, Campaign, Church, etc
    """
    user = models.ForeignKey('people.User', null=True, blank=True, on_delete=models.CASCADE)

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
    @classmethod
    def create(cls, obj, user=None):
        """
        Overwritten method to allow for the `user` parameter to be None.

        See Also
        --------
        `Activity.create`
        """
        super().create(user=user, obj=obj)


class Comment(Activity):
    content = models.TextField()

    @classmethod
    def create(cls, obj, user, comment):
        cls.objects.create(user=user, content_object=obj, comment=comment)
