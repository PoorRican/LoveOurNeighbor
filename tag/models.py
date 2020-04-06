from django.db import models


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def process_tags(cls, obj, tag_str):
        _tags = str(tag_str).split(', ')
        # TODO: somehow ignore case from user input, but preserve case in existing...
        if _tags:
            # TODO: have smart tag selection (tags selected by description)
            for t in _tags:
                if t:
                    _t, _ = cls.objects.get_or_create(name=t)
                    obj.tags.add(_t)
        obj.save()
