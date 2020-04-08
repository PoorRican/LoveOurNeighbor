# Generated by Django 3.0.4 on 2020-04-08 18:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('campaign', '0001_initial'),
        ('ministry', '0001_initial'),
        ('tag', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='ministry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to='ministry.MinistryProfile'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='campaigns', to='tag.Tag'),
        ),
    ]
