# Generated by Django 3.0.4 on 2020-04-08 18:29

from django.db import migrations, models
import frontend.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MinistryProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('verified', models.BooleanField(default=False)),
                ('address', models.CharField(max_length=256, unique=True)),
                ('phone_number', models.CharField(max_length=20, unique=True)),
                ('website', models.URLField(unique=True)),
                ('founded', models.DateField(blank=True, null=True)),
                ('pub_date', models.DateField(auto_now_add=True, verbose_name='Date Created')),
                ('staff', models.SmallIntegerField(default=1)),
                ('description', models.TextField(blank=True, null=True)),
                ('profile_img', models.ImageField(blank=True, default='img/blank_profile.jpg', null=True, upload_to=frontend.utils.generic_profile_img_dir, verbose_name='Profile Image')),
                ('banner_img', models.ImageField(blank=True, null=True, upload_to=frontend.utils.generic_banner_img_dir, verbose_name='Banner Image')),
                ('facebook', models.URLField(blank=True, null=True, verbose_name='Facebook')),
                ('instagram', models.URLField(blank=True, null=True, verbose_name='Instagram')),
                ('youtube', models.URLField(blank=True, null=True, verbose_name='YouTube')),
                ('twitter', models.URLField(blank=True, null=True, verbose_name='Twitter')),
            ],
        ),
    ]
