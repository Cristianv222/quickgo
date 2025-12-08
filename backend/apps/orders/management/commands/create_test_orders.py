"""
Comando de Django para crear pedidos de prueba
Ubicación: backend/apps/orders/management/commands/create_test_orders.py
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg  # ← AGREGAR ESTA LÍNEA
from apps.orders.models import Order, OrderItem, OrderStatusHistory, OrderRating
from apps.restaurants.models import Restaurant
from apps.products.models import Product, ProductExtra, ProductOption
from apps.users.models import Customer, Driver
from decimal import Decimal
import random
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea pedidos de prueba con diferentes estados y datos realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Número de pedidos a crear (default: 50)'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['PENDING', 'CONFIRMED', 'PREPARING', 'READY', 'PICKED_UP', 
                     'IN_TRANSIT', 'DELIVERED', 'CANCELLED', 'ALL'],
            default='ALL',
            help='Estado específico de pedidos o ALL para variado'
        )
        parser.add_argument(
            '--days-back',
            type=int,
            default=30,
            help='Generar pedidos de los últimos N días (default: 30)'
        )

    def handle(self, *args, **options):
        count = options['count']
        status_filter = options['status']
        days_back = options['days_back']
        
        self.stdout.write(self.style.WARNING(f'Creando {count} pedidos de prueba...'))
        
        # Verificar que existen datos necesarios
        if not self._verify_data():
            return
        
        # Obtener datos base
        customers = list(User.objects.filter(user_type='CUSTOMER'))
        restaurants = list(Restaurant.objects.filter(status='APPROVED'))
        drivers = list(User.objects.filter(user_type='DRIVER'))
        
        if not customers or not restaurants:
            self.stdout.write(self.style.ERROR('No hay suficientes clientes o restaurantes'))
            return
        
        created_count = 0
        
        for i in range(count):
            try:
                # Seleccionar datos aleatorios
                customer = random.choice(customers)
                restaurant = random.choice(restaurants)
                
                # Obtener productos del restaurante
                products = list(restaurant.products.filter(
                    is_active=True,
                    is_available=True
                ))
                
                if not products:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ {restaurant.name} no tiene productos disponibles')
                    )
                    continue
                
                # Determinar estado del pedido
                if status_filter == 'ALL':
                    order_status = self._get_random_status()
                else:
                    order_status = status_filter
                
                # Crear pedido
                order = self._create_order(
                    customer=customer,
                    restaurant=restaurant,
                    products=products,
                    status=order_status,
                    days_back=days_back
                )
                
                # Asignar conductor si es necesario
                if order_status in ['PICKED_UP', 'IN_TRANSIT', 'DELIVERED'] and drivers:
                    order.driver = random.choice(drivers)
                    order.save()
                
                # Actualizar timestamps según estado
                self._update_timestamps(order, order_status)
                
                # Crear rating si está entregado (50% de probabilidad)
                if order_status == 'DELIVERED' and random.random() > 0.5:
                    self._create_rating(order)
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Pedido #{order.order_number} - {order.get_status_display()}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error creando pedido {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Proceso completado: {created_count}/{count} pedidos creados')
        )
        
        # Mostrar resumen
        self._show_summary()
    
    def _verify_data(self):
        """Verificar que existen los datos necesarios"""
        customers = User.objects.filter(user_type='CUSTOMER').count()
        restaurants = Restaurant.objects.filter(status='APPROVED').count()
        products = Product.objects.filter(is_active=True, is_available=True).count()
        
        if customers == 0:
            self.stdout.write(self.style.ERROR('❌ No hay clientes registrados'))
            self.stdout.write('Ejecuta: python manage.py createsuperuser o crea clientes manualmente')
            return False
        
        if restaurants == 0:
            self.stdout.write(self.style.ERROR('❌ No hay restaurantes aprobados'))
            self.stdout.write('Ejecuta: python manage.py create_test_restaurants')
            return False
        
        if products == 0:
            self.stdout.write(self.style.ERROR('❌ No hay productos disponibles'))
            self.stdout.write('Ejecuta: python manage.py create_test_menus')
            return False
        
        self.stdout.write(self.style.SUCCESS(f'✓ Datos verificados: {customers} clientes, {restaurants} restaurantes, {products} productos'))
        return True
    
    def _get_random_status(self):
        """Obtener estado aleatorio con pesos realistas"""
        statuses = [
            ('DELIVERED', 50),    # 50% entregados
            ('PENDING', 10),      # 10% pendientes
            ('CONFIRMED', 10),    # 10% confirmados
            ('PREPARING', 8),     # 8% preparando
            ('READY', 5),         # 5% listos
            ('PICKED_UP', 5),     # 5% recogidos
            ('IN_TRANSIT', 7),    # 7% en tránsito
            ('CANCELLED', 5),     # 5% cancelados
        ]
        
        status_list = []
        for status, weight in statuses:
            status_list.extend([status] * weight)
        
        return random.choice(status_list)
    
    def _create_order(self, customer, restaurant, products, status, days_back):
        """Crear un pedido con items"""
        
        # Obtener perfil del cliente
        customer_profile = getattr(customer, 'customer_profile', None)
        if not customer_profile:
            # Crear perfil si no existe
            Customer.objects.create(
                user=customer,
                address=self._get_random_address(),
                latitude=Decimal(str(random.uniform(0.810, 0.820))),
                longitude=Decimal(str(random.uniform(-77.720, -77.710)))
            )
            customer_profile = customer.customer_profile
        
        # Crear pedido
        order = Order.objects.create(
            customer=customer,
            restaurant=restaurant,
            status=status,
            delivery_address=customer_profile.address or self._get_random_address(),
            delivery_reference=random.choice([
                'Casa blanca con portón negro',
                'Edificio azul, segundo piso',
                'Junto al parque',
                'Frente a la farmacia',
                'Casa esquinera',
                ''
            ]),
            delivery_latitude=customer_profile.latitude or Decimal(str(random.uniform(0.810, 0.820))),
            delivery_longitude=customer_profile.longitude or Decimal(str(random.uniform(-77.720, -77.710))),
            payment_method=random.choice(['CASH', 'CARD', 'WALLET']),
            is_paid=random.choice([True, False]) if status != 'CANCELLED' else False,
            special_instructions=random.choice([
                '',
                'Sin cebolla por favor',
                'Bien cocido',
                'Con bastante ají',
                'Llamar al llegar',
                'Dejar en la puerta',
                'Tocar el timbre',
            ]),
            tip=Decimal(random.choice(['0.00', '0.50', '1.00', '1.50', '2.00', '3.00'])),
            service_fee=Decimal('0.50'),
            estimated_preparation_time=random.randint(20, 45)
        )
        
        # Calcular distancia
        order.calculate_distance()
        
        # Agregar items al pedido (2-5 productos)
        num_items = random.randint(2, 5)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        for product in selected_products:
            # Obtener extras disponibles
            extras = list(product.extras.filter(is_available=True))
            selected_extras = []
            
            # 30% probabilidad de agregar extras
            if extras and random.random() > 0.7:
                num_extras = random.randint(1, min(3, len(extras)))
                for extra in random.sample(extras, num_extras):
                    selected_extras.append({
                        'id': extra.id,
                        'name': extra.name,
                        'price': str(extra.price),
                        'quantity': 1
                    })
            
            # Obtener opciones disponibles
            option_groups = product.option_groups.prefetch_related('options')
            selected_options = []
            
            for group in option_groups:
                available_options = list(group.options.filter(is_available=True))
                if available_options:
                    option = random.choice(available_options)
                    selected_options.append({
                        'group_id': group.id,
                        'group': group.name,
                        'option_id': option.id,
                        'option': option.name,
                        'price_modifier': str(option.price_modifier)
                    })
            
            # Crear item
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_description=product.description,
                product_image=product.image.url if product.image else '',
                unit_price=product.price,
                quantity=random.randint(1, 3),
                selected_extras=selected_extras,
                selected_options=selected_options,
                special_notes=random.choice([
                    '',
                    'Sin cebolla',
                    'Poco picante',
                    'Bien cocido',
                    'Sin tomate',
                ])
            )
        
        # Calcular totales
        order.calculate_totals()
        
        # Aplicar descuento aleatorio (10% de probabilidad)
        if random.random() > 0.9:
            order.discount = Decimal(str(random.uniform(1.0, 5.0)))
            order.coupon_code = f"PROMO{random.randint(100, 999)}"
            order.save()
        
        # Generar fecha de creación aleatoria
        days_ago = random.randint(0, days_back)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        created_date = timezone.now() - timedelta(
            days=days_ago,
            hours=hours_ago,
            minutes=minutes_ago
        )
        
        order.created_at = created_date
        order.save()
        
        # Crear historial inicial
        OrderStatusHistory.objects.create(
            order=order,
            status='PENDING',
            notes='Pedido creado',
            changed_by=customer,
            created_at=created_date
        )
        
        return order
    
    def _update_timestamps(self, order, status):
        """Actualizar timestamps según el estado del pedido"""
        base_time = order.created_at
        
        if status in ['CONFIRMED', 'PREPARING', 'READY', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED']:
            # Confirmado (5-15 min después)
            order.confirmed_at = base_time + timedelta(minutes=random.randint(5, 15))
            order.estimated_delivery_time = order.confirmed_at + timedelta(
                minutes=order.estimated_preparation_time + order.restaurant.delivery_time_max
            )
            
            OrderStatusHistory.objects.create(
                order=order,
                status='CONFIRMED',
                notes='Pedido confirmado por el restaurante',
                created_at=order.confirmed_at
            )
        
        if status in ['PREPARING', 'READY', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED']:
            # Preparando (10-20 min después de confirmar)
            order.preparing_at = order.confirmed_at + timedelta(minutes=random.randint(10, 20))
            
            OrderStatusHistory.objects.create(
                order=order,
                status='PREPARING',
                notes='Restaurante preparando el pedido',
                created_at=order.preparing_at
            )
        
        if status in ['READY', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED']:
            # Listo (15-30 min después de empezar a preparar)
            order.ready_at = order.preparing_at + timedelta(minutes=random.randint(15, 30))
            
            OrderStatusHistory.objects.create(
                order=order,
                status='READY',
                notes='Pedido listo para recoger',
                created_at=order.ready_at
            )
        
        if status in ['PICKED_UP', 'IN_TRANSIT', 'DELIVERED']:
            # Recogido (5-15 min después de estar listo)
            order.picked_up_at = order.ready_at + timedelta(minutes=random.randint(5, 15))
            
            OrderStatusHistory.objects.create(
                order=order,
                status='PICKED_UP',
                notes='Pedido recogido por el conductor',
                created_at=order.picked_up_at
            )
        
        if status in ['IN_TRANSIT', 'DELIVERED']:
            # En tránsito (2-5 min después de recoger)
            in_transit_time = order.picked_up_at + timedelta(minutes=random.randint(2, 5))
            
            OrderStatusHistory.objects.create(
                order=order,
                status='IN_TRANSIT',
                notes='Pedido en camino',
                created_at=in_transit_time
            )
        
        if status == 'DELIVERED':
            # Entregado (10-25 min después de recoger)
            order.delivered_at = order.picked_up_at + timedelta(minutes=random.randint(10, 25))
            
            # Marcar como pagado si no lo estaba
            if not order.is_paid:
                order.is_paid = True
                order.payment_date = order.delivered_at
            
            OrderStatusHistory.objects.create(
                order=order,
                status='DELIVERED',
                notes='Pedido entregado al cliente',
                created_at=order.delivered_at
            )
            
            # Actualizar estadísticas
            order.restaurant.total_orders += 1
            order.restaurant.total_revenue += order.total
            order.restaurant.save()
            
            if hasattr(order.customer, 'customer_profile'):
                profile = order.customer.customer_profile
                profile.total_orders += 1
                profile.total_spent += order.total
                profile.save()
            
            if order.driver and hasattr(order.driver, 'driver_profile'):
                profile = order.driver.driver_profile
                profile.total_deliveries += 1
                profile.total_earnings += order.delivery_fee + order.tip
                profile.save()
        
        if status == 'CANCELLED':
            # Cancelado (aleatorio entre 5-60 min después de crear)
            order.cancelled_at = base_time + timedelta(minutes=random.randint(5, 60))
            order.cancellation_reason = random.choice([
                'CUSTOMER_REQUEST',
                'RESTAURANT_UNAVAILABLE',
                'OUT_OF_STOCK',
                'WRONG_ADDRESS',
                'OTHER'
            ])
            order.cancellation_notes = random.choice([
                'Cliente solicitó cancelación',
                'Restaurante sin stock',
                'Dirección incorrecta',
                'Cliente no contesta',
                'Cambio de planes',
            ])
            order.cancelled_by = order.customer
            
            OrderStatusHistory.objects.create(
                order=order,
                status='CANCELLED',
                notes=f'Cancelado: {order.cancellation_notes}',
                created_at=order.cancelled_at
            )
        
        order.save()
    
    def _create_rating(self, order):
        """Crear calificación para un pedido entregado"""
        overall_rating = random.randint(3, 5)  # Mayoría de ratings positivos
        
        # Aspectos positivos y negativos
        positive_aspects = [
            'Rápido',
            'Buena presentación',
            'Comida caliente',
            'Conductor amable',
            'Bien empaquetado'
        ]
        
        negative_aspects = [
            'Llegó frío',
            'Faltó cubiertos',
            'Tardó mucho',
            'Empaque roto',
            'Sin servilletas'
        ]
        
        liked = random.sample(positive_aspects, random.randint(1, 3))
        disliked = random.sample(negative_aspects, random.randint(0, 2)) if overall_rating < 5 else []
        
        comments = [
            '¡Excelente servicio! Todo llegó perfecto.',
            'Muy buena comida, volveré a ordenar.',
            'El tiempo de entrega fue bueno.',
            'Todo estuvo delicioso.',
            'Buena atención del conductor.',
            'La comida llegó caliente y en buen estado.',
            'Cumplió con mis expectativas.',
            'Tardó un poco pero valió la pena.',
        ]
        
        OrderRating.objects.create(
            order=order,
            overall_rating=overall_rating,
            food_rating=random.randint(max(1, overall_rating - 1), 5),
            delivery_rating=random.randint(max(1, overall_rating - 1), 5),
            driver_rating=random.randint(max(1, overall_rating - 1), 5) if order.driver else None,
            driver_comment=random.choice([
                'Muy amable',
                'Rápido y eficiente',
                'Buena actitud',
                'Puntual',
                ''
            ]) if order.driver else '',
            comment=random.choice(comments),
            would_order_again=overall_rating >= 4,
            liked_aspects=liked,
            disliked_aspects=disliked
        )
        
        order.is_rated = True
        order.save()
    
    def _get_random_address(self):
        """Generar dirección aleatoria"""
        streets = [
            'Av. Principal', 'Calle Central', 'Calle Bolívar', 'Av. Colon',
            'Calle Sucre', 'Av. 10 de Agosto', 'Calle García Moreno',
            'Av. Panamericana', 'Calle Olmedo', 'Av. Universitaria'
        ]
        
        return f"{random.choice(streets)} {random.randint(100, 999)}, Tulcán"
    
    def _show_summary(self):
        """Mostrar resumen de pedidos creados"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('RESUMEN DE PEDIDOS CREADOS'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        total = Order.objects.count()
        
        self.stdout.write(f'\n📊 Total de pedidos en el sistema: {total}')
        
        self.stdout.write('\n📈 Por estado:')
        for status_choice in Order.Status.choices:
            count = Order.objects.filter(status=status_choice[0]).count()
            percentage = (count / total * 100) if total > 0 else 0
            self.stdout.write(f'  • {status_choice[1]}: {count} ({percentage:.1f}%)')
        
        self.stdout.write('\n💳 Por método de pago:')
        for payment_choice in Order.PaymentMethod.choices:
            count = Order.objects.filter(payment_method=payment_choice[0]).count()
            self.stdout.write(f'  • {payment_choice[1]}: {count}')
        
        paid_count = Order.objects.filter(is_paid=True).count()
        self.stdout.write(f'\n💰 Pedidos pagados: {paid_count}')
        
        rated_count = Order.objects.filter(is_rated=True).count()
        self.stdout.write(f'⭐ Pedidos calificados: {rated_count}')
        
        total_revenue = Order.objects.filter(status='DELIVERED').aggregate(
            total=Sum('total')
        )['total'] or 0
        
        self.stdout.write(f'💵 Ingresos totales (entregados): ${total_revenue:.2f}')
        
        avg_order = Order.objects.filter(status='DELIVERED').aggregate(
            avg=Avg('total')
        )['avg'] or 0
        
        self.stdout.write(f'📊 Valor promedio de pedido: ${avg_order:.2f}')
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60 + '\n'))