from django.db import models

from users.models import User, Contact


STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class Shop(models.Model):
    name = models.CharField('Название', max_length=50)
    url = models.URLField('Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Владелец',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    state = models.BooleanField('Статус получения заказов', default=True)

    # TODO: filename

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


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
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'],
                                    name='unique_product_info'),
        ]


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


class Order(models.Model):
    dt = models.DateTimeField(auto_now_add=True)
    status = models.CharField('Статус', choices=STATE_CHOICES, max_length=15)
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='orders', blank=True,
                             on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, verbose_name='Контакт',
                                blank=True, null=True,
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)

    # @property
    # def sum(self):
    #     return self.ordered_items.aggregate(total=Sum("quantity"))["total"]


class OrderItem(models.Model):
    quantity = models.PositiveIntegerField('Количество')
    order = models.ForeignKey(Order, verbose_name='Заказ',
                              related_name='ordered_items', blank=True,
                              on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo,
                                     verbose_name='Информация о продукте',
                                     related_name='ordered_items', blank=True,
                                     on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'],
                                    name='unique_order_item'),
        ]
