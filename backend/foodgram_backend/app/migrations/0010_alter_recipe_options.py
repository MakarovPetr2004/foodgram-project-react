# Generated by Django 3.2.3 on 2023-09-13 19:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0009_alter_favoriterecipe_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes',
                     'ordering': ('-created',), 'verbose_name': 'Рецепт',
                     'verbose_name_plural': 'Рецепты'},
        ),
    ]
