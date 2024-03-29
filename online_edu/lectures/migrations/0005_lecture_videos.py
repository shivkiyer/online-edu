# Generated by Django 4.2.5 on 2024-03-18 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_contents', '0005_remove_videocontent_lectures_alter_videocontent_name'),
        ('lectures', '0004_alter_lecture_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='videos',
            field=models.ManyToManyField(related_name='lectures', to='video_contents.videocontent'),
        ),
    ]
