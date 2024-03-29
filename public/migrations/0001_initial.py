# Generated by Django 3.0.4 on 2020-04-08 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='FaqSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(unique=True)),
                ('title', models.CharField(max_length=256)),
                ('content', models.TextField()),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='MessageOfTheDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='The title to be displayed.', max_length=32)),
                ('message', models.TextField()),
                ('display', models.BooleanField(default=True, help_text='Do you want this message to be displayed on the homepage?', unique=True)),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('edit_date', models.DateTimeField(auto_now=True, verbose_name='Date Modified')),
            ],
        ),
        migrations.CreateModel(
            name='SocialMediaLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('class_attr', models.CharField(max_length=32, verbose_name='Element Class Attribute')),
                ('url', models.URLField(verbose_name='Social Media URL')),
            ],
        ),
        migrations.CreateModel(
            name='WebsiteText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=32, unique=True)),
                ('location', models.CharField(blank=True, max_length=128, null=True, verbose_name='Where is the text located?')),
                ('text', models.TextField()),
            ],
        ),
    ]
