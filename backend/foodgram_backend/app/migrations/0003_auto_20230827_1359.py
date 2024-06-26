# Generated by Django 3.2.3 on 2023-08-27 13:59

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0002_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'default_related_name': 'recipe_ingredient',
                     'verbose_name': 'Ингредиент рецепта',
                     'verbose_name_plural': 'Ингредиенты рецепта'},
        ),
        migrations.AlterModelOptions(
            name='recipetag',
            options={'default_related_name': 'recipe_tag',
                     'verbose_name': 'Тег рецепта',
                     'verbose_name_plural': 'Теги рецепта'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/images'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_ingredient', to='app.ingredient'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_ingredient', to='app.recipe'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_tag', to='app.recipe'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='tag',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_tag', to='app.tag'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, unique=True, validators=[
                django.core.validators.MinLengthValidator(7)]),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
