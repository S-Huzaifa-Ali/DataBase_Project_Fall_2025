from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, Customer, Order, OrderItem, Review, Payment
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database...')

        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Books', 'description': 'Books and literature'},
            {'name': 'Home & Garden', 'description': 'Home improvement and garden supplies'},
            {'name': 'Sports', 'description': 'Sports equipment and accessories'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(**cat_data)
            categories[cat.name] = cat
            if created:
                self.stdout.write(f'Created category: {cat.name}')

        # Create products
        products_data = [
            {'name': 'Laptop', 'category': 'Electronics', 'price': '999.99', 'stock': 50, 'description': 'High-performance laptop for work and gaming'},
            {'name': 'Smartphone', 'category': 'Electronics', 'price': '699.99', 'stock': 100, 'description': 'Latest smartphone with advanced features'},
            {'name': 'Wireless Headphones', 'category': 'Electronics', 'price': '149.99', 'stock': 75, 'description': 'Noise-cancelling wireless headphones'},
            {'name': 'T-Shirt', 'category': 'Clothing', 'price': '19.99', 'stock': 200, 'description': 'Comfortable cotton t-shirt'},
            {'name': 'Jeans', 'category': 'Clothing', 'price': '49.99', 'stock': 150, 'description': 'Classic denim jeans'},
            {'name': 'Python Programming', 'category': 'Books', 'price': '39.99', 'stock': 80, 'description': 'Learn Python programming from scratch'},
            {'name': 'Fiction Novel', 'category': 'Books', 'price': '14.99', 'stock': 120, 'description': 'Bestselling fiction novel'},
            {'name': 'Garden Tools Set', 'category': 'Home & Garden', 'price': '79.99', 'stock': 40, 'description': 'Complete set of garden tools'},
            {'name': 'Basketball', 'category': 'Sports', 'price': '29.99', 'stock': 60, 'description': 'Professional basketball'},
            {'name': 'Yoga Mat', 'category': 'Sports', 'price': '24.99', 'stock': 90, 'description': 'Non-slip yoga mat'},
        ]

        products = []
        for prod_data in products_data:
            cat_name = prod_data.pop('category')
            stock = prod_data.pop('stock')
            prod, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': categories[cat_name],
                    'price': Decimal(prod_data['price']),
                    'stock_quantity': stock,
                    'description': prod_data['description'],
                    'is_active': True
                }
            )
            products.append(prod)
            if created:
                self.stdout.write(f'Created product: {prod.name}')

        # Create users and customers
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
        ]

        customers = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.username}')

            customer, created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'phone': '555-0100',
                    'address': '123 Main St',
                    'city': 'New York',
                    'postal_code': '10001',
                    'country': 'USA'
                }
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'Created customer: {customer}')

        # Create sample orders
        if customers and products:
            order, created = Order.objects.get_or_create(
                customer=customers[0],
                defaults={
                    'status': 'delivered',
                    'total_amount': Decimal('1149.98'),
                    'shipping_address': '123 Main St, New York, NY 10001'
                }
            )
            if created:
                OrderItem.objects.create(order=order, product=products[0], quantity=1, price=products[0].price)
                OrderItem.objects.create(order=order, product=products[2], quantity=1, price=products[2].price)
                Payment.objects.create(
                    order=order,
                    payment_method='credit_card',
                    payment_status='completed',
                    amount=order.total_amount,
                    transaction_id='TXN123456'
                )
                self.stdout.write(f'Created order: {order}')

        # Create sample reviews
        if customers and products:
            Review.objects.get_or_create(
                product=products[0],
                customer=customers[0],
                defaults={
                    'rating': 5,
                    'comment': 'Excellent laptop! Very fast and reliable.'
                }
            )
            Review.objects.get_or_create(
                product=products[1],
                customer=customers[1],
                defaults={
                    'rating': 4,
                    'comment': 'Great phone, but battery could be better.'
                }
            )

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
