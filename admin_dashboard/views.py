from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .decorators import unnauthenticate_user, allowed_users, authorize_seller
from django.contrib import messages
from datetime import datetime, timezone
from .forms import CategoryForm, TagForm, ProductForm, VariantForm, AttachmentForm, UserForm, UserProfileForm, CreditCardForm, AddressForm, OptionTypeForm, OptionValueForm
from products.models import Category, Tag, Product, Variant, Attachment, OptionType, OptionValue
from orders.models import Order, LineItem
from accounts.models import IDCardsAttachment, ProofBusinessAttachment, User, WishlistedProduct, Address, UserProduct, CreditCard
from endless_admin.translations import get_translations

@login_required(login_url='login')
@allowed_users()
def home(request):
  context = {'section_active': 'dashboards', 'lang': get_user_locale(request)}
  if request.user.is_admin():
    context['recent_orders'] = LineItem.objects.select_related('order', 'variant')
  elif request.user.is_seller():
    seller_product_variants = Variant.objects.filter(product__in=request.user.products())
    context['recent_orders'] = LineItem.objects.select_related('variant').filter(variant__in=seller_product_variants)
  return render(request, 'dashboard/home.html', context)

@login_required(login_url='login')
@allowed_users()
def profile(request):
  user = request.user
  form = UserProfileForm(instance=request.user)
  
  if request.method == 'POST':
    form = UserProfileForm(request.POST, instance=request.user)

    if form.is_valid():
      form.save()
      messages.success(request, get_translations('Account was updated successfully', get_user_locale(request)))
    else:
      messages.error(request, get_translations('Account updation failed', get_user_locale(request)))
  return render(request, 'dashboard/profile.html', {'form': form, 'user': user, 'lang': get_user_locale(request)})

#Users CRUD ================
@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def users(request):
  users = User.objects.all()
  context = {'users': users, 'section_active': 'users', 'lang': get_user_locale(request)}
  return render(request, 'dashboard/users/index.html', context)

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def users_wishlisted_products(request):
  wishlisted_products = WishlistedProduct.objects.all()
  context = {'wishlisted_products': wishlisted_products, 'section_active': 'users_wishlisted_products', 'lang': get_user_locale(request)}
  return render(request, 'dashboard/users/wishlisted_products.html', context)

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def new_user(request):
  form = UserForm()
  if request.method == 'POST':
    form = UserForm(request.POST)
    if form.is_valid(): 
      form.save()
      messages.success(request, get_translations('User created successfully', get_user_locale(request)))
      return redirect('users_list')
  return render(request, 'dashboard/users/new.html', {'form': form, 'section_active': 'users', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def edit_user(request, pk):
  user = User.objects.get(pk=pk)
  try:
    idcard = IDCardsAttachment.objects.filter(company=user).values('file').first().get('file')
    pob = ProofBusinessAttachment.objects.filter(company=user).values('file').first().get('file')
  except:
    idcard = "N/A"
    pob = "N/A"
  form = UserForm(instance=user)
  if request.method == 'POST':
    form = UserForm(request.POST, instance=user)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('User updated successfully', get_user_locale(request)))
      return redirect('users_list')
  return render(request, 'dashboard/users/edit.html', {'form': form, 'user': user,'idcard':idcard,'pob':pob, 'section_active': 'users', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def user_addresses(request, pk):
  user = User.objects.get(pk=pk)
  addresses = Address.objects.filter(user=user).all()
  return render(request, 'dashboard/users/addresses/index.html', { 'user': user, 'addresses':addresses, 'section_active': 'addresses', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def new_user_address(request, pk):
  user = User.objects.get(pk=pk)
  form = AddressForm()
  if request.method == 'POST':
    form = AddressForm(request.POST)
    if form.is_valid():
      form.save()
      user.addresses.add(form.instance)
      messages.success(request, get_translations('User address created successfully', get_user_locale(request)))
      return redirect('user_addresses', user.id)
  return render(request, 'dashboard/users/addresses/new.html', {'form': form, 'user': user, 'section_active': 'addresses', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def edit_user_address(request, pk, address_id):
  user = User.objects.get(pk=pk)
  address = user.addresses.get(pk=address_id)
  form = AddressForm(instance=address)
  if request.method == 'POST':
    form = AddressForm(request.POST, instance=address)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('User address updated successfully', get_user_locale(request)))
      return redirect('user_addresses', user.id)
  return render(request, 'dashboard/users/addresses/edit.html', {'form': form, 'user': user, 'section_active': 'addresses', 'address': address, 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def credit_cards(request, pk):
  user = User.objects.get(pk=pk)
  credit_cards = CreditCard.objects.filter(user=user).all()
  return render(request, 'dashboard/users/credit_cards/index.html', { 'user': user, 'credit_cards':credit_cards, 'section_active': 'credit_cards', 'lang': get_user_locale(request)})

#Orders
@login_required(login_url='login')
@allowed_users()
def orders(request):
  item_id = request.GET.get('oid')
  if item_id:
    item = LineItem.objects.get(pk=item_id)
    return render(request, 'dashboard/orders/show.html', {"item": item, 'section_active': 'orders', 'lang': get_user_locale(request)})
  else:
    if request.user.is_admin():
      order_items = LineItem.objects.select_related('variant')
      return render(request, 'dashboard/orders/index.html', {"order_items": order_items, 'section_active': 'orders', 'lang': get_user_locale(request)})
    elif request.user.is_seller():
      seller_product_variants = Variant.objects.filter(product__in=request.user.products())
      order_items = LineItem.objects.select_related('variant').filter(variant__in=seller_product_variants)
      return render(request, 'dashboard/orders/index.html', {"order_items": order_items, 'section_active': 'orders', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
def mark_item_shipped(request, pk):
  if request.method == 'POST':
    try:
      print("dispatched at ",request.POST)
      item = LineItem.objects.get(id=pk)
      
      parsed_dispatched_at =  datetime.strptime(request.POST.get('dispatched_at'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
      if item.dispatched:
        messages.error(request, get_translations('Order item already shipped', get_user_locale(request)))
        return redirect('/dashboards/orders?oid=' + str(pk))
      else:
        if item.created_at >  parsed_dispatched_at:
          messages.error(request, get_translations('Dispatched At can not be before order placed at date', get_user_locale(request)))
          return redirect('/dashboards/orders?oid=' + str(pk))
        else:
          item.dispatched_at = parsed_dispatched_at
          item.dispatched = True
          item.courier_agency = request.POST.get('courier_agency')
          item.tracking_number = request.POST.get('tracking_number')
          item.save()
          messages.success(request, get_translations('Item marked as shipped successfully', get_user_locale(request)))
          return redirect('/dashboards/orders?oid=' + str(pk))
    except:
      messages.error(request, get_translations('Invalid Order Item', get_user_locale(request)))
      return redirect('/dashboards/orders?oid=' + str(pk))
  else:
    messages.error(request, get_translations('Invalid Action Performed', get_user_locale(request)))
    return redirect('/dashboards/orders?oid=' + str(pk))

#Option Types CRUD ================
@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def option_types(request):
  option_types = OptionType.objects.all()
  context = {'option_types': option_types, 'section_active': 'option_types', 'lang': get_user_locale(request)}
  return render(request, 'dashboard/option_types/index.html', context)

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def new_option_type(request):
  form = OptionTypeForm()
  if request.method == 'POST':
    form = OptionTypeForm(request.POST)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('OptionType created successfully', get_user_locale(request)))
      return redirect('option_types_list')
  return render(request, 'dashboard/option_types/new.html', {'form': form, 'section_active': 'option_types', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def edit_option_type(request, pk):
  option_type = OptionType.objects.get(pk=pk)
  form = OptionTypeForm(instance=option_type)
  if request.method == 'POST':
    form = OptionTypeForm(request.POST, instance=option_type)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('OptionType updated successfully', get_user_locale(request)))
      return redirect('option_types_list')
  return render(request, 'dashboard/option_types/edit.html', {'form': form, 'option_type': option_type, 'section_active': 'option_types', 'lang': get_user_locale(request)})

#Option Values CRUD ================
@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def option_values(request):
  option_values = OptionValue.objects.all()
  if request.GET.get('option_type') is not None:
    option_values = option_values.filter(option_type=request.GET.get('option_type'))
    context = {'option_values': option_values, 'section_active': 'option_values', 'lang': get_user_locale(request)}
    return render(request, 'dashboard/option_values/index.html', context)
  else:
    context = {'option_values': option_values, 'section_active': 'option_values', 'lang': get_user_locale(request)}
    return render(request, 'dashboard/option_values/index.html', context)

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def new_option_value(request):
  form = OptionValueForm()
  if request.method == 'POST':
    form = OptionValueForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('OptionValue created successfully', get_user_locale(request)))
      return redirect('option_values_list')
  return render(request, 'dashboard/option_values/new.html', {'form': form, 'section_active': 'option_values', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def edit_option_value(request, pk):
  option_value = OptionValue.objects.get(pk=pk)
  form = OptionValueForm(instance=option_value)
  if request.method == 'POST':
    form = OptionValueForm(request.POST, instance=option_value)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('OptionValue updated successfully', get_user_locale(request)))
      return redirect('option_values_list')
  return render(request, 'dashboard/option_values/edit.html', {'form': form, 'option_value': option_value, 'section_active': 'option_values', 'lang': get_user_locale(request)})

#Categories CRUD ================
@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def categories(request):
  categories = Category.objects.all()
  context = {'categories': categories, 'section_active': 'categories', 'lang': get_user_locale(request)}
  return render(request, 'dashboard/categories/index.html', context)

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def new_category(request):
  form = CategoryForm()
  if request.method == 'POST':
    form = CategoryForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('Category created successfully', get_user_locale(request)))
      return redirect('categories_list')
  return render(request, 'dashboard/categories/new.html', {'form': form, 'section_active': 'categories', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def edit_category(request, slug):
  category = Category.objects.get(slug=slug)
  form = CategoryForm(instance=category)
  if request.method == 'POST':
    form = CategoryForm(request.POST, request.FILES, instance=category)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('Category updated successfully', get_user_locale(request)))
      return redirect('categories_list')
  return render(request, 'dashboard/categories/edit.html', {'form': form, 'category': category, 'section_active': 'categories', 'lang': get_user_locale(request)})


#Tags CRUD =================================
@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def tags(request):
  tags = Tag.objects.all()
  context = {'tags': tags, 'section_active': 'tags', 'lang': get_user_locale(request)}
  return render(request, 'dashboard/tags/index.html', context)

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def new_tag(request):
    form = TagForm()
    if request.method == 'POST':
      form = TagForm(request.POST)
      if form.is_valid():
        form.save()
        messages.success(request, get_translations('Tag created successfully', get_user_locale(request)))
        return redirect('tags_list')
    return render(request, 'dashboard/tags/new.html', {'form': form, 'section_active': 'tags', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
@authorize_seller()
def edit_tag(request, slug):
  tag = Tag.objects.get(slug=slug)
  form = TagForm(instance=tag)
  if request.method == 'POST':
    tag = Tag.objects.get(slug=slug)
    form = TagForm(request.POST, instance=tag)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('Tag updated successfully', get_user_locale(request)))
      return redirect('tags_list')
  return render(request, 'dashboard/tags/edit.html', {'form': form, 'tag': tag, 'section_active': 'tags', 'lang': get_user_locale(request)})

#Products CRUD =================================
@login_required(login_url='login')
@allowed_users()
def products(request):
  print("\n\n\n\nUser ",request.user.is_seller(),"Products ",request.user.products())
  products = request.user.products() if request.user.is_seller() else Product.objects.all()
  context = {'products': products, 'section_active': 'products', 'lang': get_user_locale(request)}
  return render(request, 'dashboard/products/index.html', context)

@login_required(login_url='login')
@allowed_users()
def new_product(request):
  users = User.objects.filter(user_type='Seller')
  form = ProductForm()
  if request.method == 'POST':
    form = ProductForm(request.POST)
    if form.is_valid():
      form.save()
      user_product = UserProduct(user_id=request.POST.get('user'), product=form.instance)
      user_product.save()
      messages.success(request, get_translations('Product created successfully', get_user_locale(request)))
      return redirect('products_list')
  return render(request, 'dashboard/products/new.html', {'form': form, 'users': users, 'section_active': 'products', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
def edit_product(request, slug):
  product = Product.objects.get(slug=slug)
  form = ProductForm(instance=product)
  if request.method == 'POST':
    form = ProductForm(request.POST, instance=product)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('Product updated successfully', get_user_locale(request)))
      return redirect('products_list')
  return render(request, 'dashboard/products/edit.html', {'form': form, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)})

#Product Variants CRUD =================================
@login_required(login_url='login')
@allowed_users()
def product_variants(request, slug):
  product = Product.objects.get(slug=slug)
  variants = Variant.objects.filter(product=product)
  print("Variants ",variants)
  context = {'variants': variants, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)}
  return render(request, 'dashboard/products/variants/index.html', context)

@login_required(login_url='login')
@allowed_users()
def new_product_variant(request, slug):
  print("\n\n\nNew product variant slug ",slug)
  product = Product.objects.get(slug=slug)
  option_values = OptionValue.objects.filter(option_type=product.option_type)
  print("Option values ", option_values)
  form = VariantForm()

  if request.method == 'POST':
    form = VariantForm(request.POST)
    print("Variant form ",form.data)
    if form.is_valid():
      
      print("Variant form ",form)
      form.instance.option_value = OptionValue.objects.get(pk=request.POST.get('option_value'))
      form.save()
      messages.success(request, get_translations('Product variant created successfully', get_user_locale(request)))
      return redirect('product_variants_list', product.slug)
  return render(request, 'dashboard/products/variants/new.html', {'form': form, 'option_values': option_values, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
def edit_product_variant(request, slug, id):
  product = Product.objects.get(slug=slug)
  option_values = OptionValue.objects.filter(option_type=product.option_type)
  variant = Variant.objects.get(pk=id)
  form = VariantForm(instance=variant)
  
  if request.method == 'POST':
    form = VariantForm(request.POST, instance=variant)
    if form.is_valid():
      form.instance.option_value = OptionValue.objects.get(pk=request.POST.get('option_value'))
      form.save()
      messages.success(request, get_translations('Product variant updated successfully', get_user_locale(request)))
      return redirect('product_variants_list', product.slug)
  return render(request, 'dashboard/products/variants/edit.html', {'form': form, 'option_values': option_values, 'product': product, 'section_active': 'products', 'variant': variant, 'lang': get_user_locale(request)})

#Product Images CRUD =================================
@login_required(login_url='login')
@allowed_users()
def product_attachments(request, slug):
  product = Product.objects.get(slug=slug)
  attachments = Attachment.objects.filter(product=product).values()
  print("Attachments ", attachments)
  context = {'attachments': attachments, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)}
  return render(request, 'dashboard/products/attachments/index.html', context)

@login_required(login_url='login')
@allowed_users()
def new_product_attachment(request, slug):
  product = Product.objects.get(slug=slug)
  form = AttachmentForm()
  if request.method == 'POST':
    form = AttachmentForm(request.POST, request.FILES)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('Product attachment created successfully', get_user_locale(request)))
      return redirect('product_attachments_list', product.slug)
  return render(request, 'dashboard/products/attachments/new.html', {'form': form, 'product': product, 'section_active': 'products', 'lang': get_user_locale(request)})

@login_required(login_url='login')
@allowed_users()
def edit_product_attachment(request, slug, id):
  product = Product.objects.get(slug=slug)
  attachment = Attachment.objects.get(pk=id)
  form = AttachmentForm(instance=attachment)
  if request.method == 'POST':
    form = AttachmentForm(request.POST, request.FILES, instance=attachment)
    if form.is_valid():
      form.save()
      messages.success(request, get_translations('Product attachment updated successfully', get_user_locale(request)))
      return redirect('product_attachments_list', product.slug)
  return render(request, 'dashboard/products/attachments/edit.html', {'form': form, 'product': product, 'section_active': 'products', 'attachment': attachment, 'lang': get_user_locale(request)})

def get_user_locale(request):
    try:
        return request.COOKIES['locale']
    except:
        return 'en'
