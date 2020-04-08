# Generated by Django 3.0.4 on 2020-04-08 18:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import people.models
import people.utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ministry', '0001_initial'),
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=40, verbose_name='first name')),
                ('last_name', models.CharField(max_length=40, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_verified', models.BooleanField(default=people.utils.verification_required, verbose_name='verified')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('_location', models.CharField(blank=True, max_length=256, null=True, verbose_name='Location')),
                ('profile_img', models.ImageField(blank=True, default='img/blank_profile.jpg', null=True, upload_to=people.utils.user_profile_img_dir, verbose_name='Profile Image')),
                ('confirmation', models.UUIDField(blank=True, default=uuid.uuid4, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('logged_in_as', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='ministry.MinistryProfile')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'auth_user',
                'abstract': False,
            },
            managers=[
                ('objects', people.models.MyUserManager()),
            ],
        ),
    ]
