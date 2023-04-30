from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import Sum, F
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from distutils.util import strtobool
from yaml import load as load_yaml, Loader
from requests import get

from orders.models import Order
from orders.serializers import OrderSerializer
from partners.tasks import import_yaml
from products.models import Shop
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
                import_yaml(data, request.user.id)
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
