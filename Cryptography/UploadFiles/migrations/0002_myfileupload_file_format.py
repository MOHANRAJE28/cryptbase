# Generated by Django 5.0.3 on 2024-04-22 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UploadFiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='myfileupload',
            name='file_format',
            field=models.CharField(default='unknown', max_length=20),
        ),
    ]