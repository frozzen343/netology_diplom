from django.db import models

from products.models import ProductInfo
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
