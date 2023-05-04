from django.db import models

from partners.models import Shop


class Category(models.Model):
    name = models.CharField('Наименование категории', max_length=40)
    shops = models.ManyToManyField(Shop, verbose_name='Магазины',
                                   related_name='categories',
                                   blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = "Список категорий"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('Название', max_length=80)
    category = models.ForeignKey(Category, verbose_name='Категория',
                                 related_name='products',
                                 blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    model = models.CharField('Модель', max_length=80, blank=True)
    external_id = models.PositiveIntegerField('Внешний ИД')
    quantity = models.PositiveIntegerField('Количество')
    price = models.PositiveIntegerField('Цена')
    price_rrc = models.PositiveIntegerField('Рекомендуемая розничная цена')
    product = models.ForeignKey(Product, verbose_name='Продукт',
                                related_name='product_infos',
                                blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин',
                             related_name='product_infos',
                             blank=True,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        ordering = ('-model',)
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'],
                                    name='unique_product_info'),
        ]

    def __str__(self):
        return self.model


class Parameter(models.Model):
    name = models.CharField('Название', max_length=40)

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = "Список имен параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    value = models.CharField('Значение', max_length=100)
    product_info = models.ForeignKey(ProductInfo,
                                     verbose_name='Информация о продукте',
                                     related_name='product_parameters',
                                     blank=True,
                                     on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр',
                                  related_name='product_parameters',
                                  blank=True,
                                  on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'],
                                    name='unique_product_parameter'),
        ]
