"""
Comando de Django para crear restaurantes de prueba
Ubicación: backend/apps/restaurants/management/commands/create_test_restaurants.py
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.restaurants.models import (
    Restaurant, RestaurantSchedule, RestaurantReview, RestaurantGallery
)
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea restaurantes de prueba con datos completos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Número de restaurantes a crear (default: 10)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(self.style.WARNING(f'Creando {count} restaurantes de prueba...'))
        
        # Obtener usuario admin existente o crear uno nuevo
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.create_superuser(
                    username='admin_quickgo',
                    email='admin@quickgo.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='QuickGo',
                    phone='0999999999',
                )
                self.stdout.write(self.style.SUCCESS('✓ Usuario admin creado'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Usando admin existente: {admin_user.username}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error con usuario admin: {str(e)}'))
            return

        # Datos de ejemplo
        restaurants_data = [
            {
                'name': 'Pizzería Bella Napoli',
                'cuisine_type': 'PIZZA',
                'description': 'Auténtica pizza italiana con ingredientes importados y masa artesanal. Horneadas en horno de leña tradicional.',
                'coords': (0.812440, -77.717239),
                'promotion': '2x1 en pizzas familiares los martes'
            },
            {
                'name': 'Burger Master',
                'cuisine_type': 'BURGER',
                'description': 'Las mejores hamburguesas gourmet de la ciudad. Carne 100% angus y vegetales frescos.',
                'coords': (0.813562, -77.718134),
                'promotion': 'Combo especial: Hamburguesa + papas + bebida'
            },
            {
                'name': 'Sabor Ecuatoriano',
                'cuisine_type': 'ECUADORIAN',
                'description': 'Comida típica ecuatoriana. Secos, hornados, fritadas y más. Sazón casera de abuelita.',
                'coords': (0.814123, -77.719045),
                'promotion': ''
            },
            {
                'name': 'Sushi & Roll',
                'cuisine_type': 'CHINESE',
                'description': 'Sushi fresco y rolls creativos. Cocina oriental con toque moderno.',
                'coords': (0.811890, -77.716523),
                'promotion': '20% descuento en rolls'
            },
            {
                'name': 'El Asadero del Norte',
                'cuisine_type': 'GRILL',
                'description': 'Carnes a la parrilla de primera calidad. Cortes especiales y parrilladas completas.',
                'coords': (0.815234, -77.720156),
                'promotion': 'Parrillada para 2 personas'
            },
            {
                'name': 'Pollos al Carbón Don José',
                'cuisine_type': 'CHICKEN',
                'description': 'Pollos asados al carbón. Receta familiar con papas, ensalada y ají de la casa.',
                'coords': (0.810567, -77.715678),
                'promotion': 'Pollo completo + 2 bebidas'
            },
            {
                'name': 'Marisquería El Pescador',
                'cuisine_type': 'SEAFOOD',
                'description': 'Ceviches, encocados y mariscos frescos del día. Sabor costeño auténtico.',
                'coords': (0.816789, -77.721234),
                'promotion': ''
            },
            {
                'name': 'Café & Brunch House',
                'cuisine_type': 'COFFEE',
                'description': 'Café de especialidad, desayunos todo el día y postres artesanales.',
                'coords': (0.812890, -77.717890),
                'promotion': 'Happy hour 3-5pm: 2x1 en café'
            },
            {
                'name': 'Tacos & Burritos Mexicanos',
                'cuisine_type': 'MEXICAN',
                'description': 'Comida mexicana auténtica. Tacos al pastor, burritos, quesadillas y más.',
                'coords': (0.813456, -77.718567),
                'promotion': 'Martes de tacos: 3x2'
            },
            {
                'name': 'Green Life - Comida Saludable',
                'cuisine_type': 'HEALTHY',
                'description': 'Bowls saludables, smoothies, ensaladas y opciones veganas. Sin azúcar añadida.',
                'coords': (0.814567, -77.719678),
                'promotion': ''
            },
            {
                'name': 'Desayunos Doña Rosita',
                'cuisine_type': 'BREAKFAST',
                'description': 'Desayunos ecuatorianos tradicionales. Bolones, tigrillo, empanadas y más.',
                'coords': (0.811234, -77.716890),
                'promotion': ''
            },
            {
                'name': 'La Panadería Francesa',
                'cuisine_type': 'BAKERY',
                'description': 'Pan artesanal, croissants, baguettes y repostería francesa.',
                'coords': (0.815678, -77.720567),
                'promotion': '10% descuento comprando más de $10'
            },
        ]

        created_count = 0
        
        for i in range(min(count, len(restaurants_data))):
            data = restaurants_data[i]
            
            try:
                # Crear usuario dueño del restaurante
                owner_email = f"restaurant{i+1}@quickgo.com"
                owner_username = f"restaurant{i+1}"
                
                owner, created = User.objects.get_or_create(
                    email=owner_email,
                    defaults={
                        'username': owner_username,
                        'first_name': f'Dueño',
                        'last_name': f'Restaurante {i+1}',
                        'phone': f'09{random.randint(10000000, 99999999)}',
                        'user_type': User.UserType.RESTAURANT,
                        'is_verified': True,
                    }
                )
                if created:
                    owner.set_password('restaurant123')
                    owner.save()

                # Verificar si ya existe un restaurante para este usuario
                if hasattr(owner, 'restaurant_profile'):
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Restaurante ya existe para {owner.email}')
                    )
                    continue

                # Crear restaurante
                restaurant = Restaurant.objects.create(
                    user=owner,
                    name=data['name'],
                    description=data['description'],
                    cuisine_type=data['cuisine_type'],
                    phone=f'06{random.randint(2000000, 2999999)}',
                    email=owner_email,
                    address=f'Av. Principal {random.randint(100, 999)}, Tulcán',
                    address_reference=f'Cerca del parque {random.choice(["central", "norte", "sur", "La Loma"])}',
                    latitude=Decimal(str(data['coords'][0])),
                    longitude=Decimal(str(data['coords'][1])),
                    ruc=f'17{random.randint(10000000, 99999999)}001',
                    status=Restaurant.Status.APPROVED,
                    approved_at=timezone.now(),
                    approved_by=admin_user,
                    is_open=random.choice([True, True, True, False]),  # 75% abiertos
                    is_accepting_orders=True,
                    delivery_time_min=random.choice([20, 25, 30, 35]),
                    delivery_time_max=random.choice([40, 45, 50, 60]),
                    delivery_fee=Decimal(random.choice(['1.50', '2.00', '2.50', '3.00'])),
                    min_order_amount=Decimal(random.choice(['5.00', '8.00', '10.00'])),
                    free_delivery_above=Decimal(random.choice(['15.00', '20.00', '25.00', '30.00'])) if random.random() > 0.3 else None,
                    delivery_radius_km=Decimal(random.choice(['3.0', '4.0', '5.0', '6.0'])),
                    rating=Decimal(str(round(random.uniform(3.8, 5.0), 2))),
                    total_reviews=random.randint(10, 200),
                    total_orders=random.randint(50, 1000),
                    is_featured=random.random() > 0.7,  # 30% destacados
                    is_new=random.random() > 0.8,  # 20% nuevos
                    has_promotion=bool(data['promotion']),
                    promotion_text=data['promotion'],
                    accepts_cash=True,
                    accepts_card=random.random() > 0.3,
                    has_parking=random.random() > 0.6,
                    has_wifi=random.random() > 0.5,
                    is_eco_friendly=random.random() > 0.7,
                    commission_rate=Decimal('15.00'),
                )

                # Crear horarios (Lunes a Domingo)
                for day in range(1, 8):
                    if day in [6, 7]:  # Fin de semana - horarios especiales
                        opening = random.choice(['08:00', '09:00', '10:00'])
                        closing = random.choice(['22:00', '23:00', '00:00'])
                    else:  # Entre semana
                        opening = random.choice(['08:00', '09:00', '10:00', '11:00'])
                        closing = random.choice(['20:00', '21:00', '22:00'])
                    
                    is_closed = (day == 7 and random.random() > 0.7)  # 30% cierran domingos
                    
                    RestaurantSchedule.objects.create(
                        restaurant=restaurant,
                        day_of_week=day,
                        opening_time=opening if not is_closed else '00:00',
                        closing_time=closing if not is_closed else '00:00',
                        is_closed=is_closed
                    )

                # Crear algunas reseñas de clientes
                review_count = random.randint(3, 8)
                comments = [
                    '¡Excelente servicio! La comida llegó caliente y a tiempo.',
                    'Muy rica la comida, definitivamente volveré a pedir.',
                    'Buena calidad precio. Recomendado.',
                    'Delicioso todo, el empaquetado muy bueno.',
                    'Entrega rápida y todo perfecto.',
                    'Me encantó, superó mis expectativas.',
                    'La mejor comida de la zona, muy recomendado.',
                    'Excelente atención y sabor increíble.',
                ]
                
                for _ in range(review_count):
                    rating = random.randint(3, 5)
                    RestaurantReview.objects.create(
                        restaurant=restaurant,
                        customer=admin_user,  # Usar admin como cliente de ejemplo
                        rating=rating,
                        comment=random.choice(comments),
                        food_quality=rating,
                        delivery_time=random.randint(max(1, rating - 1), 5),
                        packaging=random.randint(max(1, rating - 1), 5),
                        is_verified=True,
                        is_visible=True,
                        created_at=timezone.now() - timezone.timedelta(days=random.randint(1, 60))
                    )

                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Restaurante creado: {restaurant.name}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creando restaurante {data["name"]}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Proceso completado: {created_count}/{count} restaurantes creados')
        )
        self.stdout.write(self.style.WARNING('\n🔑 Credenciales de acceso:'))
        self.stdout.write('  Admin: admin@quickgo.com / admin123')
        self.stdout.write('  Restaurantes: restaurant1@quickgo.com (hasta restaurant12@quickgo.com) / restaurant123')