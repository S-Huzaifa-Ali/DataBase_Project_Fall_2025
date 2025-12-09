#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_db.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()



# # Django ORM
# products = Product.objects.filter(is_active=True)

# # Translates to SQL:
# SELECT * FROM store_product 
# INNER JOIN store_category 
# ON store_product.category_id = store_category.id
# WHERE store_product.is_active = 1;



# # Django ORM
# cart_items = cart.items.all()

# # Translates to SQL:
# SELECT 
#     ci.id, ci.quantity, ci.added_at,
#     p.name, p.price, p.description
# FROM store_cartitem ci
# INNER JOIN store_cart c ON ci.cart_id = c.id
# INNER JOIN store_product p ON ci.product_id = p.id
# WHERE c.customer_id = ?;