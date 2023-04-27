from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Q, Sum, F
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from distutils.util import strtobool
from yaml import load as load_yaml, Loader
from requests import get

from orders.models import Order
from orders.serializers import OrderSerializer
from products.models import Shop, Category, ProductInfo, Product, Parameter, \
    ProductParameter
from products.serializers import ShopSerializer


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'Status': False,
                             'Error': 'Только для магазинов'},
                            status=403)

        url = request.data.get('url')
        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return Response({'Status': False, 'Error': str(e)})
            else:
                stream = get(url).content

                data = load_yaml(stream, Loader=Loader)

                shop, _ = Shop.objects.get_or_create(name=data['shop'],
                                                     user_id=request.user.id)
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(
                        id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(
                        name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(
                        product_id=product.id,
                        external_id=item['id'],
                        model=item['model'],
                        price=item['price'],
                        price_rrc=item['price_rrc'],
                        quantity=item['quantity'],
                        shop_id=shop.id
                    )
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(
                            name=name)
                        ProductParameter.objects.create(
                            product_info_id=product_info.id,
                            parameter_id=parameter_object.id,
                            value=value
                        )

                return Response({'Status': True})

        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})


class PartnerState(APIView):
    """
    Класс для работы со статусом поставщика
    """
    permission_classes = [IsAuthenticated]

    # получить текущий статус
    def get(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для магазинов'},
                            status=403)
        if not hasattr(request.user, 'shop'):
            return Response({'Status': False, 'Error': 'Магазин не найден'})

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для магазинов'},
                            status=403)
        if not hasattr(request.user, 'shop'):
            return Response({'Status': False, 'Error': 'Магазин не найден'})

        state = request.data.get('state')
        if state:
            try:
                Shop.objects.filter(user_id=request.user.id)\
                    .update(state=strtobool(state))
                return Response({'Status': True})
            except ValueError as error:
                return Response({'Status': False, 'Errors': str(error)})

        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})


class PartnerOrders(APIView):
    """
    Класс для получения заказов поставщиками
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для магазинов'},
                            status=403)

        order = Order.objects\
            .filter(
                ordered_items__product_info__shop__user_id=request.user.id)\
            .exclude(status='basket')\
            .prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter')\
            .select_related('contact')\
            .annotate(total_sum=Sum(F('ordered_items__quantity') *
                                    F('ordered_items__product_info__price')))\
            .distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)
