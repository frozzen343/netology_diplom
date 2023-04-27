from django.urls import path

from partners.views import PartnerUpdate, PartnerState, PartnerOrders

urlpatterns = [
    path('update', PartnerUpdate.as_view(), name='partner_update'),
    path('state', PartnerState.as_view(), name='partner_state'),
    path('orders', PartnerOrders.as_view(), name='partner_orders'),
]
