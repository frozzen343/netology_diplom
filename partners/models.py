from django.db import models

from users.models import User


class Shop(models.Model):
    name = models.CharField('Название', max_length=50)
    url = models.URLField('Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Владелец',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    state = models.BooleanField('Статус получения заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = "Список магазинов"
        ordering = ('-name',)

    def __str__(self):
        return self.name
