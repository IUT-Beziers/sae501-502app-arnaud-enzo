# Generated by Django 5.1.5 on 2025-01-22 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0002_agents_agent_last_seen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='packets',
            name='dst_port',
        ),
        migrations.RemoveField(
            model_name='packets',
            name='src_port',
        ),
    ]
