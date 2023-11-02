# Generated by Django 4.2.5 on 2023-11-02 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='course',
            name='is_draft',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='is_free',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='course',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
    ]
