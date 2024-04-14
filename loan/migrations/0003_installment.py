# Generated by Django 5.0.4 on 2024-04-14 18:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loan', '0002_alter_customer_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Installment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paid', models.BooleanField(default=False)),
                ('collector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loan.collector')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loan_installment', to='loan.loan')),
            ],
        ),
    ]
