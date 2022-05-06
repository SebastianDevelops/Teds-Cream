import datetime
import json
from django.template import loader
from django.shortcuts import redirect, render, get_object_or_404
from django.http import BadHeaderError, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from .models import  *
from .utils import *

# Create your views here.

def home(request):
    
    data = cartData(request)
     
    cartItems = data["cartItems"]
     
    products = Product.objects.all()
        
    water_based = Product.objects.filter(category=1)
    milk_based = Product.objects.filter(category=2)
    paleta = Product.objects.filter(category=3)
    tub = Product.objects.filter(category=4)
    featured_categories = Flavor.objects.filter(is_featured=True)

    context = {
        "products": products,
        'water_based': water_based,
        "milk_based": milk_based,
        "paleta": paleta,
        "tub": tub,
        'featured_categories': featured_categories,
        "products": products,
        "cartItems": cartItems,
        }
    
    return render(request, "store.html", context)


def product_description_redirect(request, slug):
    data = cartData(request)
     
    cartItems = data["cartItems"]
    product = get_object_or_404(Product, slug=slug)
    context = {
        "product": product,
        "cartItems": cartItems,
    }
    return render(request, "store.html", context)


def product_list(request):
    data = cartData(request)
     
    cartItems = data["cartItems"]
    product = Product.objects.all()
    context = {
      "product": product,
      "cartItems": cartItems, 
    }
    return render(request, "product-display.html", context) 



# This was taken from storefront as the urls.py did not want to render...

def product_page(request, slug):
    data = cartData(request)
     
    cartItems = data["cartItems"]
    product = get_object_or_404(Product, slug=slug)
    context = {
        "product": product,
        "cartItems": cartItems
    }
    return render(request, "product_detail.html", context)


#for cart_detail
def cart(request):
    data  = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'cart.html', context)

def checkout(request):
    data  = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems, 'shipping':True}
    return render(request, 'checkout.html', context)



def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action :', action)
    print('productId :',productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    # below line attaches the order to the given customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    # in the below line, we r using 'get_or_create' to change the values of orderItem, if it already exists
    # so, if it already exists, we don't wan't to create orderItem again, we just want to change the quantity of orderItem
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action =='add':
        # by clicking up arrow, increment orderItem by 1
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        # by clicking up arrow, decrement orderItem by 1
        orderItem.quantity = (orderItem.quantity - 1)

    # save quantity of products, for an order
    orderItem.save()

    if orderItem.quantity <= 0:
        # remove the orderItem from cart, when quantity reaches 0, or below it
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

@csrf_exempt #there is a video on a potential better solution to this



def order(request):
        data  = cartData(request)
        cartItems = data['cartItems']
        order = data['order']
        items = data['items']

        context = {'items':items, 'order':order, 'cartItems':cartItems, 'shipping':True}
    
        return render(request, "order.html", context)
    
        #fix
        #User.objects.create_superuser(username=customer, password=email, email=email)


    
def processOrder(request):
        transaction_id = datetime.datetime.now().timestamp()
        data = json.loads(request.body)
        #fix
        #User = get_user_model()
        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)

        else:
            # guestOrder function is present in utils.py
            customer, order = guestOrder(request, data)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        
        name = data['form']['name']
        email = data['form']['email']
        #fix
        #User.objects.create_superuser(username=customer, password=email, email=email)
        
        address = data['shipping']['address']
        city = data['shipping']['city']
        state = data['shipping']['state']
        zipcode = data['shipping']['zipcode']
        items = cookieCart(request)
        content = f"STREET: {address}, CITY: {city}, PROVINCE: {state}, ZIPCODE: {zipcode}"
        order_items = f"The order contains {items}"
        html_message = loader.render_to_string(
    'mail.html',
    {
        "customer":customer,
        "content":content,
        "order": order,
        "items":items,
        "email":email,
        "total":total,
    }
)
        
        email = EmailMessage(
            f"You have a new order from {customer} with the order number {order}",
            html_message,
            email,
            ["sebastiandevelops@gmail.com"],
            headers = {"Reply-To": email
            }
        )
        email.send()
       
    
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
                )

        return JsonResponse("Payment submitted...",safe=False)
    