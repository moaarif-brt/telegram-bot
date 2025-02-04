# Generated by Django 5.1.5 on 2025-02-01 10:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_symbol', models.CharField(help_text='Symbol of the token (e.g., BTC, ETH)', max_length=10, unique=True, verbose_name='Token Symbol')),
                ('token_name', models.CharField(help_text='Full name of the token (e.g., Bitcoin, Ethereum)', max_length=100, verbose_name='Token Name')),
                ('exchange', models.CharField(help_text='Exchange where the token is listed (e.g., Binance, Coinbase)', max_length=50, verbose_name='Exchange Platform')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the token was added')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp when the token was last updated')),
                ('user', models.ForeignKey(help_text='User who owns this token', on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL, verbose_name='Token Owner')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
                'ordering': ['-created_at'],
            },
        ),
    ]
