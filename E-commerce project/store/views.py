from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Review, Customer, Payment

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_active=True)[:8]
    context = {
        'categories': categories,
        'featured_products': featured_products,
    }
    return render(request, 'store/home.html', context)

def product_list(request):
    products = Product.objects.filter(is_active=True)
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def cart_view(request):
    customer = get_object_or_404(Customer, user=request.user)
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_items = cart.items.all()
    total = sum(item.get_subtotal() for item in cart_items)
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    customer = get_object_or_404(Customer, user=request.user)
    cart, created = Cart.objects.get_or_create(customer=customer)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('product_detail', pk=product_id)

@login_required
def order_list(request):
    customer = get_object_or_404(Customer, user=request.user)
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    context = {'orders': orders}
    return render(request, 'store/order_list.html', context)

@login_required
def order_detail(request, pk):
    customer = get_object_or_404(Customer, user=request.user)
    order = get_object_or_404(Order, pk=pk, customer=customer)
    context = {'order': order}
    return render(request, 'store/order_detail.html', context)

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            context = {'error': 'Invalid username or password'}
            return render(request, 'store/login.html', context)
    
    return render(request, 'store/login.html')

def user_signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if password1 != password2:
            context = {'error': 'Passwords do not match'}
            return render(request, 'store/signup.html', context)
        
        if User.objects.filter(username=username).exists():
            context = {'error': 'Username already exists'}
            return render(request, 'store/signup.html', context)
        
        if User.objects.filter(email=email).exists():
            context = {'error': 'Email already registered'}
            return render(request, 'store/signup.html', context)
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        
        # Create customer profile
        Customer.objects.create(user=user)
        
        # Log the user in
        login(request, user)
        messages.success(request, f'Welcome to ShopHub, {user.username}!')
        return redirect('home')
    
    return render(request, 'store/signup.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

@login_required
def checkout(request):
    customer = get_object_or_404(Customer, user=request.user)
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart')
    
    total = sum(item.get_subtotal() for item in cart_items)
    
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        payment_method = request.POST.get('payment_method')
        notes = request.POST.get('notes', '')
        
        # Create shipping address string
        shipping_address = f"{full_name}\n{address}\n{city}, {postal_code}\n{country}\nPhone: {phone}"
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            status='pending',
            total_amount=total,
            shipping_address=shipping_address,
            notes=notes
        )
        
        # Create order items from cart
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Update product stock
            product = cart_item.product
            product.stock_quantity -= cart_item.quantity
            product.save()
        
        # Create payment record
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            payment_status='pending',
            amount=total
        )
        
        # Clear cart
        cart_items.delete()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_success', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)

@login_required
def order_success(request, order_id):
    customer = get_object_or_404(Customer, user=request.user)
    order = get_object_or_404(Order, pk=order_id, customer=customer)
    context = {'order': order}
    return render(request, 'store/order_success.html', context)
