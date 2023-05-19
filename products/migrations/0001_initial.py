# Generated by Django 4.2 on 2023-05-18 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('partners', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Наименование категории')),
                ('shops', models.ManyToManyField(blank=True, related_name='categories', to='partners.shop', verbose_name='Магазины')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Список категорий',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Имя параметра',
                'verbose_name_plural': 'Список имен параметров',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Название')),
                ('category', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.category', verbose_name='Категория')),
            ],
            options={
                'verbose_name': 'Продукт',
                'verbose_name_plural': 'Список продуктов',
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='ProductInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField(blank=True, max_length=80, verbose_name='Модель')),
                ('external_id', models.PositiveIntegerField(verbose_name='Внешний ИД')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество')),
                ('price', models.PositiveIntegerField(verbose_name='Цена')),
                ('price_rrc', models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')),
                ('product', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_infos', to='products.product', verbose_name='Продукт')),
                ('shop', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_infos', to='partners.shop', verbose_name='Магазин')),
            ],
            options={
                'verbose_name': 'Информация о продукте',
                'verbose_name_plural': 'Информационный список о продуктах',
                'ordering': ('-model',),
            },
        ),
        migrations.CreateModel(
            name='ProductParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100, verbose_name='Значение')),
                ('parameter', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='products.parameter', verbose_name='Параметр')),
                ('product_info', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='products.productinfo', verbose_name='Информация о продукте')),
            ],
            options={
                'verbose_name': 'Параметр',
                'verbose_name_plural': 'Список параметров',
            },
        ),
        migrations.AddConstraint(
            model_name='productparameter',
            constraint=models.UniqueConstraint(fields=('product_info', 'parameter'), name='unique_product_parameter'),
        ),
        migrations.AddConstraint(
            model_name='productinfo',
            constraint=models.UniqueConstraint(fields=('product', 'shop', 'external_id'), name='unique_product_info'),
        ),
    ]
