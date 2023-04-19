from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
# from django_rest_passwordreset.tokens import get_token_generator


STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Магазин'),
    ('buyer', 'Покупатель'),

)


class UserManager(BaseUserManager):
    """
    Миксин для управления пользователями
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Стандартная модель пользователей
    """
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField('Компания', max_length=40, blank=True)
    position = models.CharField('Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. '
                    'Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists.")},
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'),
    )
    type = models.CharField('Тип пользователя', choices=USER_TYPE_CHOICES,
                            max_length=5, default='buyer')

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)


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
    #  TODO: зачем м2м ?
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


class Contact(models.Model):
    #  TODO: Отличия от кода
    address = models.CharField('Адрес', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=20)
    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.phone} {self.address}'


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

#  TODO: tokens?
# class ConfirmEmailToken(models.Model):
#     class Meta:
#         verbose_name = 'Токен подтверждения Email'
#         verbose_name_plural = 'Токены подтверждения Email'
#
#     @staticmethod
#     def generate_key():
#         """ generates a pseudo random code using os.urandom
#         and binascii.hexlify """
#         return get_token_generator().generate_token()
#
#     user = models.ForeignKey(
#         User,
#         related_name='confirm_email_tokens',
#         on_delete=models.CASCADE,
#         verbose_name=_("The User which is associated
#                         to this password reset token")
#     )
#
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         verbose_name=_("When was this token generated")
#     )
#
#     # Key field, though it is not the primary key of the model
#     key = models.CharField(
#         _("Key"),
#         max_length=64,
#         db_index=True,
#         unique=True
#     )
#
#     def save(self, *args, **kwargs):
#         if not self.key:
#             self.key = self.generate_key()
#         return super(ConfirmEmailToken, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return "Password reset token for user {user}".format(user=self.user)
