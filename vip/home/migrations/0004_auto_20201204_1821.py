# Generated by Django 3.1b1 on 2020-12-04 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_auto_20201204_1633'),
    ]

    operations = [
        migrations.RenameField(
            model_name='choice',
            old_name='noans',
            new_name='votes',
        ),
        migrations.AddField(
            model_name='poll',
            name='n1',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='poll',
            name='n2',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='poll',
            name='n3',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='poll',
            name='n4',
            field=models.IntegerField(default=0),
        ),
    ]