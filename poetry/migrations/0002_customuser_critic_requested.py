# Generated by Django 5.1.4 on 2025-01-02 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poetry', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='critic_requested',
            field=models.BooleanField(default=False),
        ),
    ]