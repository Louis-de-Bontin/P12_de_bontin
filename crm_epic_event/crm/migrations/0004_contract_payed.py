# Generated by Django 4.0.1 on 2022-02-15 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0003_event_finished_alter_contract_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='payed',
            field=models.BooleanField(default=False),
        ),
    ]
