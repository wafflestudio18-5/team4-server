# Generated by Django 3.1.4 on 2020-12-24 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("question", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userquestion",
            name="bookmark_at",
            field=models.DateTimeField(null=True),
        ),
    ]
