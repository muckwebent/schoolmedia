# Generated by Django 5.0.6 on 2024-06-14 14:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_remove_page_followers_page_followers'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='followers',
        ),
        migrations.AddField(
            model_name='page',
            name='followers',
            field=models.ManyToManyField(blank=True, related_name='page_followers', to=settings.AUTH_USER_MODEL),
        ),
    ]
