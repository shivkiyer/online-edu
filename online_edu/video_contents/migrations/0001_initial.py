# Generated by Django 4.2.5 on 2024-05-31 19:35

from django.db import migrations, models
import django.db.models.deletion
import video_contents.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Video name', max_length=300)),
                ('name_en', models.CharField(default='Video name', max_length=300, null=True)),
                ('name_de', models.CharField(default='Video name', max_length=300, null=True)),
                ('video_file', models.FileField(max_length=300, upload_to=video_contents.models.video_file_path)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='courses.course')),
            ],
        ),
    ]
