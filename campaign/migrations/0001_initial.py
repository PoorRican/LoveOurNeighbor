# Generated by Django 3.0.4 on 2020-04-08 18:29

import campaign.utils
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True)),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('start_date', models.DateField(default=datetime.date.today, verbose_name='start date')),
                ('end_date', models.DateField(verbose_name='end date')),
                ('goal', models.PositiveIntegerField(verbose_name='goal')),
                ('content', models.TextField(blank=True, null=True)),
                ('banner_img', models.ImageField(blank=True, null=True, upload_to=campaign.utils.campaign_banner_dir, verbose_name='Banner Image')),
            ],
        ),
    ]
