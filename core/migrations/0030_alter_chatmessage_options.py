# Generated by Django 5.0.6 on 2024-06-16 15:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_remove_page_followers_page_followers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chatmessage',
            options={'ordering': ['-date'], 'verbose_name_plural': 'Chat Message'},
        ),
    ]
