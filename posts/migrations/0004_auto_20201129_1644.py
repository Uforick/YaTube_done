# Generated by Django 2.2.9 on 2020-11-29 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20201129_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=None, related_name='posts', to='posts.Group'),
        ),
    ]
