import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.restaurants.models import Restaurant
from apps.users.models import User
from decimal import Decimal

# Obtener el usuario admin
admin = User.objects.filter(is_superuser=True).first()

if not admin:
    print("Error: No se encontró usuario admin")
    exit(1)

# Crear restaurantes de prueba
restaurants_data = [
    {
        'user': admin,
        'name': 'Pizza Bella',
        'description': 'Las mejores pizzas artesanales de la ciudad con ingredientes frescos',
        'cuisine_type': 'PIZZA',
        'phone': '0999111222',
        'email': 'pizzabella@quickgo.com',
        'address': 'Av. Principal 123, Centro',
        'latitude': Decimal('-0.180653'),
        'longitude': Decimal('-78.467834'),
        'ruc': '1234567890001',
        'status': 'APPROVED',
        'delivery_time_min': 25,
        'delivery_time_max': 35,
        'delivery_fee': Decimal('2.50'),
        'min_order_amount': Decimal('10.00'),
        'rating': Decimal('4.5'),
        'is_featured': True,
    },
    {
        'user': admin,
        'name': 'Burger House',
        'description': 'Hamburguesas gourmet y papas fritas crujientes',
        'cuisine_type': 'BURGER',
        'phone': '0999333444',
        'email': 'burgerhouse@quickgo.com',
        'address': 'Calle Comercio 456, Norte',
        'latitude': Decimal('-0.181234'),
        'longitude': Decimal('-78.468123'),
        'ruc': '1234567890002',
        'status': 'APPROVED',
        'delivery_time_min': 20,
        'delivery_time_max': 30,
        'delivery_fee': Decimal('2.00'),
        'min_order_amount': Decimal('8.00'),
        'rating': Decimal('4.7'),
        'is_featured': True,
    },
    {
        'user': admin,
        'name': 'Sushi Express',
        'description': 'Sushi fresco y rolls especiales preparados al momento',
        'cuisine_type': 'CHINESE',
        'phone': '0999555666',
        'email': 'sushiexpress@quickgo.com',
        'address': 'Plaza Central 789, Sur',
        'latitude': Decimal('-0.182345'),
        'longitude': Decimal('-78.469234'),
        'ruc': '1234567890003',
        'status': 'APPROVED',
        'delivery_time_min': 30,
        'delivery_time_max': 45,
        'delivery_fee': Decimal('3.00'),
        'min_order_amount': Decimal('15.00'),
        'rating': Decimal('4.8'),
    },
    {
        'user': admin,
        'name': 'Tacos Locos',
        'description': 'Tacos mexicanos auténticos con sabor casero',
        'cuisine_type': 'MEXICAN',
        'phone': '0999777888',
        'email': 'tacoslocos@quickgo.com',
        'address': 'Av. Libertad 321, Este',
        'latitude': Decimal('-0.183456'),
        'longitude': Decimal('-78.470345'),
        'ruc': '1234567890004',
        'status': 'APPROVED',
        'delivery_time_min': 15,
        'delivery_time_max': 25,
        'delivery_fee': Decimal('1.50'),
        'min_order_amount': Decimal('7.00'),
        'rating': Decimal('4.6'),
        'is_new': True,
    },
]

created_count = 0
for data in restaurants_data:
    try:
        restaurant, created = Restaurant.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            created_count += 1
            print(f"✓ Creado: {restaurant.name} - Rating: {restaurant.rating}")
        else:
            print(f"- Ya existe: {restaurant.name}")
    except Exception as e:
        print(f"✗ Error al crear {data['name']}: {e}")

print(f"\n{'='*50}")
print(f"Total restaurantes en BD: {Restaurant.objects.count()}")
print(f"Nuevos creados: {created_count}")
print(f"{'='*50}")
