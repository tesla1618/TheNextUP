# Generated by Django 4.1.3 on 2023-03-09 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_matchresult_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchresult',
            name='added',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
