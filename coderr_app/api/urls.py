from django.urls import path


from .views import OfferListView, OfferDetailView, OfferDetailItemView, BaseInfoView, \
                    OrderListView, OrderDetailView, OrderCountView, CompletedOrderCountView, \
                    ReviewListCreateView, ReviewDetailViewSet

"""
URL configuration for the Coderr API.

This module defines all endpoint routes for offers, orders, reviews,
and base information. Each path maps to a corresponding class-based view
that handles the request logic.
"""

urlpatterns = [
    path('offers/', OfferListView.as_view(), name='offer-list'),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('offerdetails/<int:pk>/', OfferDetailItemView.as_view(), name='offer-detail-item'),

    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', CompletedOrderCountView.as_view(), name='completed-order-count'),

    path('reviews/', ReviewListCreateView.as_view(), name='reviews'),
    path('reviews/<int:pk>/', ReviewDetailViewSet.as_view(), name='review-detail'),
   
    path('base-info/', BaseInfoView.as_view(), name='base-info'),
]


