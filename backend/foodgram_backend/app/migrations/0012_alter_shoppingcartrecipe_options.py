# Generated by Django 3.2.3 on 2023-09-14 17:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0011_auto_20230913_1923'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shoppingcartrecipe',
            options={'verbose_name': 'Рецепт в корзине',
                     'verbose_name_plural': 'Рецепты в корзинах'},
        ),
    ]
