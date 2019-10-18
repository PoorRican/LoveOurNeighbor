from django.db import models

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @classmethod
    def process_tags(cls, obj, tag_str):
        _tags = str(tag_str).lower().split(',')
        if _tags:
            # TODO: have smart tag selection (tags selected by description)
            for t in _tags:
                if not len(t):
                    continue
                elif t[0] == ' ':
                    t = t[1:]
                elif t[-1] == ' ':
                    t = t[:-1]
                if t:
                    _t, _ = cls.objects.get_or_create(name=t)
                    obj.tags.add(_t)
        obj.save()