from django.db import IntegrityError
from django.db.models import Sum, F, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json

from diplom.celery import send_email
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer, OrderItemSerializer


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """
    permission_classes = [IsAuthenticated]

    # получить корзину
    def get(self, request, *args, **kwargs):
        basket = Order.objects\
            .filter(user_id=request.user.id, status='basket')\
            .prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter')\
            .annotate(total_sum=Sum(F('ordered_items__quantity') *
                                    F('ordered_items__product_info__price')))\
            .distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    # редактировать корзину
    def post(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return Response(
                    {'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(
                    user_id=request.user.id, status='basket')
                objects_created = 0
                for order_item in items_dict:
                    order_item.update({'order': basket.id})
                    serializer = OrderItemSerializer(data=order_item)
                    if serializer.is_valid():
                        try:
                            serializer.save()
                        except IntegrityError as error:
                            return Response({'Status': False,
                                             'Errors': str(error)})
                        else:
                            objects_created += 1
                    else:
                        return Response({'Status': False,
                                         'Errors': serializer.errors})

                    return Response({'Status': True,
                                     'Создано объектов': objects_created})
                return Response({'Status': False,
                                 'Errors': ('Не указаны все необходимые '
                                            'аргументы')})

    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            items_list = items_sting.split(',')
            basket, _ = Order.objects.get_or_create(user_id=request.user.id,
                                                    status='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in items_list:
                if order_item_id.isdigit():
                    query |= Q(order_id=basket.id, id=order_item_id)
                    objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return Response({'Status': True,
                                 'Удалено объектов': deleted_count})
        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})

    # добавить позиции в корзину
    def put(self, request, *args, **kwargs):
        items_sting = request.data.get('items')
        if items_sting:
            try:
                items_dict = load_json(items_sting)
            except ValueError:
                return Response(
                    {'Status': False, 'Errors': 'Неверный формат запроса'})
            else:
                basket, _ = Order.objects.get_or_create(
                    user_id=request.user.id, status='basket')
                objects_updated = 0
                for order_item in items_dict:
                    if (type(order_item['id']) == int
                            and type(order_item['quantity']) == int):
                        objects_updated += OrderItem.objects\
                                    .filter(order_id=basket.id,
                                            id=order_item['id'])\
                                    .update(quantity=order_item['quantity'])

                return Response({'Status': True,
                                 'Обновлено объектов': objects_updated})
        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})


class OrderView(APIView):
    """
    Класс для получения и размешения заказов пользователями
    """
    permission_classes = [IsAuthenticated]

    # получить мои заказы
    def get(self, request, *args, **kwargs):
        order = Order.objects\
            .filter(user_id=request.user.id).exclude(status='basket')\
            .prefetch_related(
                'ordered_items__product_info__product__category',
                'ordered_items__product_info__product_parameters__parameter')\
            .select_related('contact')\
            .annotate(total_sum=Sum(F('ordered_items__quantity') *
                                    F('ordered_items__product_info__price')))\
            .distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):
        if {'id', 'contact'}.issubset(request.data):
            try:
                is_updated = Order.objects.filter(
                    user_id=request.user.id, id=request.data['id']).update(
                    contact_id=request.data['contact'],
                    status='new')
            except IntegrityError as error:
                return Response({'Status': False,
                                 'Errors': error})
            else:
                if is_updated:
                    send_email('Обновление статуса заказа',
                               'Заказ сформирован',
                               [request.user.email])
                    return Response({'Status': True})

        return Response({'Status': False,
                         'Errors': 'Не указаны все необходимые аргументы'})
