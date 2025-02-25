# Generated by Django 5.1.6 on 2025-02-25 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_remove_shipping_full_name_shipping_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipping',
            name='company_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='shipping',
            name='email',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='shipping',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]
