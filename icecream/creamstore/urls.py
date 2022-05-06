from django.urls import path
from .views import  home, product_list, product_page, cart, updateItem, processOrder, order, product_description_redirect

urlpatterns =[
    path("", home, name="home"),
    path('""/<slug:slug>/', product_description_redirect, name="product_detail"),
    path("ice-creams/", product_list, name="product_list"),
    path("ice-creams/<slug:slug>/", product_page, name="product_detail"),
    path('cart/', cart, name="cart"),
	path('order/', order, name="order"),
    path('update_item/', updateItem, name="update_item"),
    path('process_order/', processOrder, name="process_order"),
]