# Generated by Django 3.0.6 on 2020-07-15 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebKart', '0003_contact'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_json', models.CharField(max_length=5000)),
                ('name', models.CharField(default='', max_length=100)),
                ('email', models.CharField(default='', max_length=100)),
                ('address', models.CharField(default='', max_length=200)),
                ('city', models.CharField(default='', max_length=100)),
                ('state', models.CharField(default='', max_length=100)),
                ('zip_code', models.CharField(default='', max_length=100)),
            ],
        ),
    ]
