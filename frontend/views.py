import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

from accounts.models import Address, User, WishlistedProduct
from products.models import Product, Variant, Category, Tag
from orders.models import Order, LineItem, Cart, CartItem

import stripe

from .forms import UserForm

# Create your views here.
def home(request):

    cart = get_cart(request)
    product_categories = Category.objects.all().order_by('?')[:8]
    countries = settings.COUNTRY_CHOICES
    products_query = Product.objects.filter(featured=True, is_active=True, approved=True)
    
    context = {'page_title': 'Home', 'cart':cart, 'categories': product_categories, 'products': products_query, 'countries': countries, 'lang': get_user_locale(request)}
    return render(request, 'frontend/home.html', context)

@login_required(login_url='login')
def profile(request):
    product_categories = Category.objects.all().order_by('?')[:8]
    user = request.user
    form = UserForm(instance=request.user)
  
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Account was updated successfully')
            return redirect('frontend_user_profile')
    return render(request, 'frontend/users/profile.html', {'categories': product_categories, 'form': form, 'user': user, 'cart': get_cart(request), 'lang': get_user_locale(request)})

@login_required(login_url='login')
def change_password(request):
    product_categories = Category.objects.all().order_by('?')[:8]
    user = request.user
    if request.method == 'POST':
        try:
            user = User.objects.get(email=request.POST.get(request.user.email), password=request.POST.get('current_password'))
            user.password = request.POST.get('new_password')
            user.save()
            messages.success(request, 'Account password was updated successfully')

            return redirect('frontend_user_profile')
        except:
            messages.error(request, 'Invalid current password')
            return redirect('frontend_user_profile')
    return render(request, 'frontend/users/change_password.html', {'categories': product_categories, 'lang': get_user_locale(request), 'cart': get_cart(request)})

def products(request):
    category = request.GET.get('category')
    sort_order = request.GET.get('sort_order')
    products_query = Product.objects.filter(is_active=True, approved=True)
    tag = request.GET.get('tag')
    search_query = request.GET.get('q').strip() if request.GET.get('q') is not None else "".strip()
    if category !='None' and category is not None:
        products_query = products_query.filter(category__slug=category)
    if tag != 'None' and tag is not None:
        products_query = products_query.filter(search_tags__in=[tag])
    if search_query is not None and search_query != '':
        products_query = products_query.filter(name__icontains=search_query)
    products = products_query

    if sort_order is not None:
        sort_string = "name" if sort_order == 'ascending' else "-name"
        products = products.order_by(sort_string)
    categories = Category.objects.all()
    tags = Tag.objects.all()

    return render(request, 'frontend/products/index.html', {'tag':tag, 'lang': get_user_locale(request), 'category':category, 'products': products, 'categories': categories, 'tags': tags, 'q': search_query, 'page_title': 'Products', 'cart': get_cart(request)})

def product(request, slug):
    product_categories = Category.objects.all().order_by('?')[:8]
    try:
        product = Product.objects.get(is_active=True, approved=True, slug=slug)
    except:
        messages.error(request, 'Invalid product')
        return redirect('products')
    return render(request, 'frontend/products/show.html', { 'categories': product_categories, 'lang': get_user_locale(request), 'product':product, 'cart': get_cart(request), 'page_title': product.name, 'variants': product_variants(request, product)})    

def cart(request):
    product_categories = Category.objects.all().order_by('?')[:8]
    cart = get_cart(request)
    page_title = 'Cart'
    return render(request, 'frontend/orders/cart.html', {'categories': product_categories, 'lang': get_user_locale(request), 'cart':cart, 'page_title': page_title})

def add_item_to_cart(request):
    cart = get_cart(request)
    
    print("Product variant ",request.POST['variant'])
    variant = Variant.objects.get(pk=request.POST['variant'])
    item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, option_type=variant.product.option_type.name, option_value=variant.option_value.value)
    item.quantity = request.POST['quantity']
    if int(item.quantity) > variant.stock:
        messages.error(request, 'Insufficient stock!')
    else:
        item.price = int(item.quantity) * item.variant.price
        messages.success(request, 'Item added to cart successfully.')
        item.save()

    return redirect('cart')

def update_cart_item(request, pk):
    cart = get_cart(request)
    cart_item = CartItem.objects.get(pk=pk)
    cart_item.quantity = int(request.POST['quantity'])

    if cart_item.quantity > cart_item.variant.stock:
        messages.error(request, 'Insufficient stock!')
    else:
        cart_item.price = int(cart_item.quantity) * cart_item.variant.price
        messages.success(request, 'Cart item updated successfully.')
        cart_item.save()
    return redirect('cart')

def remove_item_from_cart(request, pk):
    cart = get_cart(request)
    cart_item = CartItem.objects.get(pk=pk)
    cart_item.delete()
    messages.success(request, 'Cart item removed successfully.')

    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    product_categories = Category.objects.all().order_by('?')[:8]
    cart = get_cart(request)
    page_title = 'Checkout'
    stripe_pub_key = settings.STRIPE_PUBLISHABLE_KEY

    if cart.is_empty():
        messages.error(request, 'Cart is empty.')
        return redirect('cart')
    
    if request.method == 'POST':
        # try:
        stripe_order_token = request.POST['stripeToken']
        # charge = stripe.Charge.create(
        #     amount = int(100*cart.grand_total()),
        #     currency='usd',
        #     description='Order payment',
        #     source = stripe_order_token
        # )
        charge = {
                        "status": "succeeded",
                        "id": str(uuid.uuid4()),
                        "billing_details": {"name":"Eko Emmanuel Upo"},
                        "payment_method_details": {
                            "card": {
                                "exp_month": "11",
                                "exp_year": "2024",
                                "brand": "Master card"
                            }
                        }
                    }
        
        if charge['status'] == 'succeeded':
            order = Order(user=request.user)
            order.item_total = cart.total()
            order.total = cart.grand_total()
            order.endless_factory_cut = cart.endless_factory_cut()
            order.shipping_address = set_shipping_address_for_order(request, order)
            order.save()
            order.set_line_items_from_cart(cart)
            order.set_transaction(request.user, charge, request.POST['card_number'], True)
            cart.reset()
            messages.success(request, 'Your order has been placed successfully.')
            return redirect('user_orders')
        else:
            messages.error(request, 'Your card was declined.')
        # except Exception as e:
        #     print("\n\nException ", e)
        #     messages.error(request, 'Your card was declined.')
    
    return render(request, 'frontend/orders/checkout.html', {'categories': product_categories, 'lang': get_user_locale(request), 'cart':cart, 'page_title': page_title, 'stripe_pub_key': stripe_pub_key})

@login_required(login_url='login')
def order_status(request, pk):
    product_categories = Category.objects.all().order_by('?')[:8]
    cart = get_cart(request)
    order_item = LineItem.objects.select_related('order').filter(order__user_id=request.user.id, pk=pk).first()
    # print(product_categories,cart,order_item)
    if order_item != None:
        return render(request, 'frontend/orders/status.html', {'categories': product_categories, 'lang': get_user_locale(request), 'page_title': 'Order Item #' + str(order_item.id) + ' Status', 'cart':cart, 'order_item': order_item})
    else:
        messages.error(request, 'Invalid Order')
        return redirect('/')

@login_required(login_url='login')
def add_variant_to_wishlist(request, pk):
    product = Product.objects.get(pk=pk)
    wishlist_product, created = WishlistedProduct.objects.get_or_create(product=product, user=request.user)
    messages.success(request, 'Product added to wishlist successfully')
    return redirect('product', product.slug)

@login_required(login_url='login')
def remove_variant_from_wishlist(request, pk):
    product = Product.objects.get(pk=pk)
    wishlist_product = WishlistedProduct.objects.filter(product=product, user=request.user).first()
    if wishlist_product != None:
        wishlist_product.delete()
    messages.error(request, 'Product removed from wishlist successfully')
    return redirect('product', product.slug)

@login_required(login_url='login')
def user_orders(request):
    product_categories = Category.objects.all().order_by('?')[:8]
    order_items = LineItem.objects.select_related('order', 'variant').filter(order__user_id=request.user.id)
    page_title = 'Orders'

    return render(request, 'frontend/users/orders.html', {'categories': product_categories, 'lang': get_user_locale(request), 'order_items': order_items, 'page_title': page_title, 'cart': get_cart(request)})

@login_required(login_url='login')
def wishlisted_products(request):
    wishlisted_products = request.user.wishlistedproduct_set.all()
    page_title = 'Wishlisted Products' 
    product_categories = Category.objects.all().order_by('?')[:8]

    return render(request, 'frontend/users/wishlisted_products.html', {'categories': product_categories, 'lang': get_user_locale(request), 'wishlisted_products': wishlisted_products, 'page_title': page_title, 'cart': get_cart(request)})

@login_required(login_url='login')
def credit_cards(request):
    credit_cards = request.user.credit_cards.all()
    page_title = 'Credit Cards'

    return render(request, 'frontend/users/credit_cards.html', {'credit_cards': credit_cards, 'page_title': page_title, 'lang': get_user_locale(request), 'cart': get_cart(request)})

def set_locale(request):
  current_path = request.GET['current_path'] if request.GET['current_path'] != None else '/'
  locale = request.GET['locale'] if request.GET['locale'] != None else 'en'
  response = redirect(current_path)
  response.set_cookie('locale', locale)  
  return response
# Private methods =========================
def get_cart(request):

    if request.user.id != None:
        user = request.user
        user.cart_token = user.cart_token if user.cart_token != None  else get_random_string(length=32)
        user.save()
        cart, created = Cart.objects.get_or_create(token=user.cart_token)
    else:
        if request.session.has_key('cart_token'):
            cart, created = Cart.objects.get_or_create(token=request.session['cart_token'])
        else:
            cart = Cart.objects.create(token=get_random_string(length=32))
            request.session['cart_token'] = cart.token
    return cart

    
def set_shipping_address_for_order(request, order):
    if request.POST.get('selected_address') != 'selected_address':
        shipping_address = Address(
            first_name = request.POST.get('shipping_first_name'), 
            last_name = request.POST.get('shipping_last_name'), 
            line_1 = request.POST.get('shipping_address_line_1'), 
            line_2 = request.POST.get('shipping_address_line_2'), 
            city = request.POST.get('shipping_city'),
            state = request.POST.get('shipping_state'), 
            zipcode = request.POST.get('shipping_zipcode'), 
            country = request.POST.get('shipping_country')
        )
        shipping_address.save()
        request.user.addresses.add(shipping_address)
        return shipping_address
    else:
        return Address.objects.filter(pk=request.POST.get('selected_address')).first()
         

def product_variants(request, product):
    data = []
    for variant in product.variant_set.all():
        data.append({
            'id': variant.id,
            'option_value': variant.option_value.value,
            'stock': variant.stock
        })
    return data
    
def is_product_wishlisted(request, product):
    if request.user.is_authenticated:
        return product in request.user.wishlisted_products()
    else:
        return False

def get_user_locale(request):
  try:
    return request.COOKIES['locale']
  except:
    return 'en'