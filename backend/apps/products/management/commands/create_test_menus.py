"""
Comando de Django para crear menús de prueba para los restaurantes
Ubicación: backend/apps/products/management/commands/create_test_menus.py
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.restaurants.models import Restaurant
from apps.products.models import (
    Category, ProductTag, Product, ProductImage,
    ProductExtra, ProductOptionGroup, ProductOption, ProductReview
)
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea menús de prueba completos para los restaurantes existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--restaurant-id',
            type=int,
            help='ID específico de restaurante (opcional, si no se proporciona crea para todos)'
        )

    def handle(self, *args, **options):
        restaurant_id = options.get('restaurant_id')
        
        if restaurant_id:
            restaurants = Restaurant.objects.filter(id=restaurant_id, status=Restaurant.Status.APPROVED)
            if not restaurants.exists():
                self.stdout.write(self.style.ERROR(f'No se encontró restaurante con ID {restaurant_id}'))
                return
        else:
            restaurants = Restaurant.objects.filter(status=Restaurant.Status.APPROVED)
        
        if not restaurants.exists():
            self.stdout.write(self.style.ERROR('No hay restaurantes aprobados. Ejecuta primero create_test_restaurants'))
            return
        
        self.stdout.write(self.style.WARNING(f'Creando menús para {restaurants.count()} restaurantes...'))
        
        # Crear etiquetas globales si no existen
        self._create_tags()
        
        total_products = 0
        
        for restaurant in restaurants:
            try:
                products_created = self._create_menu_for_restaurant(restaurant)
                total_products += products_created
                self.stdout.write(
                    self.style.SUCCESS(f'✓ {restaurant.name}: {products_created} productos creados')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error en {restaurant.name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Proceso completado: {total_products} productos creados en total')
        )

    def _create_tags(self):
        """Crear etiquetas globales si no existen"""
        tags_data = [
            # Dietéticas
            {'name': 'Vegetariano', 'slug': 'vegetariano', 'tag_type': 'DIETARY', 'icon': '🌱', 'color': '#16a34a'},
            {'name': 'Vegano', 'slug': 'vegano', 'tag_type': 'DIETARY', 'icon': '🥬', 'color': '#15803d'},
            {'name': 'Sin Gluten', 'slug': 'sin-gluten', 'tag_type': 'DIETARY', 'icon': '🌾', 'color': '#ca8a04'},
            {'name': 'Bajo en Calorías', 'slug': 'bajo-calorias', 'tag_type': 'DIETARY', 'icon': '💪', 'color': '#2563eb'},
            
            # Picante
            {'name': 'Picante', 'slug': 'picante', 'tag_type': 'SPICE', 'icon': '🌶️', 'color': '#dc2626'},
            {'name': 'Muy Picante', 'slug': 'muy-picante', 'tag_type': 'SPICE', 'icon': '🔥', 'color': '#991b1b'},
            
            # Especiales
            {'name': 'Nuevo', 'slug': 'nuevo', 'tag_type': 'SPECIAL', 'icon': '✨', 'color': '#3b82f6'},
            {'name': 'Popular', 'slug': 'popular', 'tag_type': 'SPECIAL', 'icon': '⭐', 'color': '#f59e0b'},
            {'name': 'Recomendado del Chef', 'slug': 'chef-special', 'tag_type': 'SPECIAL', 'icon': '👨‍🍳', 'color': '#8b5cf6'},
            {'name': 'Especial de la Casa', 'slug': 'especial-casa', 'tag_type': 'SPECIAL', 'icon': '🏆', 'color': '#eab308'},
            
            # Alérgenos
            {'name': 'Contiene Lácteos', 'slug': 'lacteos', 'tag_type': 'ALLERGEN', 'icon': '🥛', 'color': '#64748b'},
            {'name': 'Contiene Nueces', 'slug': 'nueces', 'tag_type': 'ALLERGEN', 'icon': '🥜', 'color': '#78716c'},
        ]
        
        for tag_data in tags_data:
            ProductTag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
        
        self.stdout.write(self.style.SUCCESS('✓ Etiquetas creadas/verificadas'))

    def _create_menu_for_restaurant(self, restaurant):
        """Crear menú completo para un restaurante específico"""
        
        # Definir menús según tipo de cocina
        menu_templates = {
            'PIZZA': self._get_pizza_menu,
            'BURGER': self._get_burger_menu,
            'ECUADORIAN': self._get_ecuadorian_menu,
            'CHINESE': self._get_sushi_menu,
            'GRILL': self._get_grill_menu,
            'CHICKEN': self._get_chicken_menu,
            'SEAFOOD': self._get_seafood_menu,
            'COFFEE': self._get_coffee_menu,
            'MEXICAN': self._get_mexican_menu,
            'HEALTHY': self._get_healthy_menu,
            'BREAKFAST': self._get_breakfast_menu,
            'BAKERY': self._get_bakery_menu,
        }
        
        menu_func = menu_templates.get(restaurant.cuisine_type)
        if not menu_func:
            return 0
        
        menu_data = menu_func()
        products_created = 0
        
        # Crear categorías y productos
        for category_data in menu_data:
            category = Category.objects.create(
                restaurant=restaurant,
                name=category_data['name'],
                description=category_data.get('description', ''),
                is_active=True,
                order=category_data.get('order', 0)
            )
            
            for product_data in category_data['products']:
                product = self._create_product(restaurant, category, product_data)
                products_created += 1
        
        return products_created

    def _create_product(self, restaurant, category, product_data):
        """Crear un producto con todas sus relaciones"""
        
        # Crear producto base
        product = Product.objects.create(
            restaurant=restaurant,
            category=category,
            name=product_data['name'],
            description=product_data['description'],
            short_description=product_data.get('short_description', product_data['description'][:100]),
            price=Decimal(str(product_data['price'])),
            compare_price=Decimal(str(product_data.get('compare_price', 0))) if product_data.get('compare_price') else None,
            is_available=product_data.get('is_available', True),
            is_active=True,
            preparation_time=product_data.get('preparation_time', random.randint(10, 30)),
            calories=product_data.get('calories'),
            serving_size=product_data.get('serving_size', '1 porción'),
            is_featured=product_data.get('is_featured', random.random() > 0.7),
            is_new=product_data.get('is_new', random.random() > 0.8),
            is_popular=product_data.get('is_popular', random.random() > 0.7),
            rating=Decimal(str(round(random.uniform(4.0, 5.0), 2))),
            reviews_count=random.randint(5, 50),
            orders_count=random.randint(10, 200)
        )
        
        # Agregar etiquetas
        if 'tags' in product_data:
            tags = ProductTag.objects.filter(slug__in=product_data['tags'])
            product.tags.set(tags)
        
        # Crear extras si existen
        if 'extras' in product_data:
            for extra_data in product_data['extras']:
                ProductExtra.objects.create(
                    product=product,
                    name=extra_data['name'],
                    description=extra_data.get('description', ''),
                    price=Decimal(str(extra_data['price'])),
                    is_available=True,
                    max_quantity=extra_data.get('max_quantity', 3)
                )
        
        # Crear grupos de opciones si existen
        if 'option_groups' in product_data:
            for group_data in product_data['option_groups']:
                group = ProductOptionGroup.objects.create(
                    product=product,
                    name=group_data['name'],
                    is_required=group_data.get('is_required', True),
                    min_selections=group_data.get('min_selections', 1),
                    max_selections=group_data.get('max_selections', 1)
                )
                
                for option_data in group_data['options']:
                    ProductOption.objects.create(
                        group=group,
                        name=option_data['name'],
                        price_modifier=Decimal(str(option_data.get('price_modifier', 0))),
                        is_available=True,
                        is_default=option_data.get('is_default', False)
                    )
        
        return product

    # ========================================================================
    # MENÚS POR TIPO DE COCINA
    # ========================================================================

    def _get_pizza_menu(self):
        return [
            {
                'name': 'Pizzas Clásicas',
                'description': 'Nuestras pizzas tradicionales más populares',
                'order': 1,
                'products': [
                    {
                        'name': 'Pizza Margarita',
                        'description': 'Salsa de tomate, mozzarella fresca, albahaca y aceite de oliva extra virgen',
                        'price': 10.99,
                        'compare_price': 12.99,
                        'calories': 250,
                        'tags': ['vegetariano', 'popular'],
                        'preparation_time': 20,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Personal (8")', 'price_modifier': -2.00},
                                    {'name': 'Mediana (12")', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Familiar (16")', 'price_modifier': 4.00},
                                ]
                            },
                            {
                                'name': 'Tipo de Masa',
                                'is_required': True,
                                'options': [
                                    {'name': 'Delgada', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Gruesa', 'price_modifier': 1.00},
                                    {'name': 'Integral', 'price_modifier': 1.50},
                                ]
                            }
                        ],
                        'extras': [
                            {'name': 'Extra Queso Mozzarella', 'price': 1.50},
                            {'name': 'Queso Parmesano', 'price': 1.00},
                            {'name': 'Aceitunas', 'price': 0.75},
                            {'name': 'Champiñones', 'price': 1.00},
                        ]
                    },
                    {
                        'name': 'Pizza Pepperoni',
                        'description': 'Pepperoni premium, mozzarella y salsa de tomate especial',
                        'price': 12.99,
                        'calories': 300,
                        'tags': ['popular', 'chef-special'],
                        'preparation_time': 20,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Personal (8")', 'price_modifier': -2.00},
                                    {'name': 'Mediana (12")', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Familiar (16")', 'price_modifier': 4.00},
                                ]
                            }
                        ],
                        'extras': [
                            {'name': 'Doble Pepperoni', 'price': 2.50},
                            {'name': 'Extra Queso', 'price': 1.50},
                            {'name': 'Jalapeños', 'price': 0.75},
                        ]
                    },
                    {
                        'name': 'Pizza Hawaiana',
                        'description': 'Jamón, piña, mozzarella y salsa especial',
                        'price': 11.99,
                        'calories': 280,
                        'tags': ['popular'],
                        'preparation_time': 20,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Personal (8")', 'price_modifier': -2.00},
                                    {'name': 'Mediana (12")', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Familiar (16")', 'price_modifier': 4.00},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Pizza Cuatro Quesos',
                        'description': 'Mozzarella, parmesano, gorgonzola y queso de cabra',
                        'price': 13.99,
                        'calories': 320,
                        'tags': ['vegetariano', 'chef-special'],
                        'preparation_time': 22,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Personal (8")', 'price_modifier': -2.00},
                                    {'name': 'Mediana (12")', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Familiar (16")', 'price_modifier': 4.00},
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Pizzas Especiales',
                'description': 'Creaciones únicas de la casa',
                'order': 2,
                'products': [
                    {
                        'name': 'Pizza BBQ Pollo',
                        'description': 'Pollo, tocino, cebolla morada, salsa BBQ y mozzarella',
                        'price': 14.99,
                        'calories': 350,
                        'tags': ['especial-casa'],
                        'preparation_time': 25,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Mediana (12")', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Familiar (16")', 'price_modifier': 4.00},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Pizza Vegetariana Supreme',
                        'description': 'Pimientos, champiñones, cebolla, aceitunas, tomate y espinaca',
                        'price': 13.49,
                        'calories': 240,
                        'tags': ['vegetariano', 'bajo-calorias'],
                        'preparation_time': 22,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Mediana (12")', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Familiar (16")', 'price_modifier': 4.00},
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Bebidas',
                'description': 'Bebidas frías y calientes',
                'order': 3,
                'products': [
                    {
                        'name': 'Coca Cola',
                        'description': 'Bebida gaseosa',
                        'price': 1.50,
                        'preparation_time': 2,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Personal (350ml)', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Mediana (500ml)', 'price_modifier': 0.50},
                                    {'name': 'Familiar (1.5L)', 'price_modifier': 1.50},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Limonada Natural',
                        'description': 'Limonada fresca hecha al momento',
                        'price': 2.00,
                        'preparation_time': 5,
                        'tags': ['nuevo']
                    }
                ]
            }
        ]

    def _get_burger_menu(self):
        return [
            {
                'name': 'Hamburguesas Clásicas',
                'order': 1,
                'products': [
                    {
                        'name': 'Hamburguesa Clásica',
                        'description': 'Carne 100% angus, lechuga, tomate, cebolla, pepinillos y salsa especial',
                        'price': 6.99,
                        'calories': 450,
                        'tags': ['popular'],
                        'preparation_time': 15,
                        'option_groups': [
                            {
                                'name': 'Punto de Carne',
                                'is_required': True,
                                'options': [
                                    {'name': 'Tres Cuartos', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Término Medio', 'price_modifier': 0},
                                    {'name': 'Bien Cocido', 'price_modifier': 0},
                                ]
                            },
                            {
                                'name': 'Tamaño de Carne',
                                'is_required': True,
                                'options': [
                                    {'name': 'Simple (150g)', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Doble (300g)', 'price_modifier': 3.00},
                                    {'name': 'Triple (450g)', 'price_modifier': 5.50},
                                ]
                            }
                        ],
                        'extras': [
                            {'name': 'Queso Cheddar', 'price': 1.00},
                            {'name': 'Tocino', 'price': 1.50},
                            {'name': 'Huevo Frito', 'price': 0.75},
                            {'name': 'Aguacate', 'price': 1.25},
                            {'name': 'Jalapeños', 'price': 0.50},
                        ]
                    },
                    {
                        'name': 'Hamburguesa BBQ Bacon',
                        'description': 'Carne angus, tocino crujiente, queso cheddar, cebolla caramelizada y salsa BBQ',
                        'price': 8.99,
                        'compare_price': 10.99,
                        'calories': 580,
                        'tags': ['chef-special', 'popular'],
                        'preparation_time': 18,
                        'option_groups': [
                            {
                                'name': 'Tamaño de Carne',
                                'is_required': True,
                                'options': [
                                    {'name': 'Simple (150g)', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Doble (300g)', 'price_modifier': 3.00},
                                ]
                            }
                        ],
                        'extras': [
                            {'name': 'Extra Tocino', 'price': 1.50},
                            {'name': 'Aros de Cebolla', 'price': 2.00},
                        ]
                    },
                    {
                        'name': 'Hamburguesa Vegetariana',
                        'description': 'Hamburguesa de lentejas y quinoa, lechuga, tomate, aguacate y salsa especial',
                        'price': 7.49,
                        'calories': 320,
                        'tags': ['vegetariano', 'bajo-calorias'],
                        'preparation_time': 15,
                        'extras': [
                            {'name': 'Queso Vegano', 'price': 1.25},
                            {'name': 'Aguacate Extra', 'price': 1.00},
                        ]
                    },
                    {
                        'name': 'Hamburguesa Mexicana',
                        'description': 'Carne angus, guacamole, jalapeños, queso pepper jack, pico de gallo',
                        'price': 8.49,
                        'calories': 520,
                        'tags': ['picante', 'especial-casa'],
                        'preparation_time': 18
                    }
                ]
            },
            {
                'name': 'Acompañamientos',
                'order': 2,
                'products': [
                    {
                        'name': 'Papas Fritas',
                        'description': 'Papas fritas crujientes con sal marina',
                        'price': 2.99,
                        'preparation_time': 8,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Regular', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Grande', 'price_modifier': 1.50},
                                ]
                            },
                            {
                                'name': 'Sabor',
                                'is_required': False,
                                'options': [
                                    {'name': 'Natural', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'BBQ', 'price_modifier': 0.50},
                                    {'name': 'Queso', 'price_modifier': 0.75},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Aros de Cebolla',
                        'description': 'Aros de cebolla empanizados y fritos',
                        'price': 3.49,
                        'preparation_time': 10
                    },
                    {
                        'name': 'Nuggets de Pollo',
                        'description': '8 unidades de nuggets crujientes',
                        'price': 4.99,
                        'preparation_time': 12,
                        'option_groups': [
                            {
                                'name': 'Salsa',
                                'is_required': True,
                                'max_selections': 2,
                                'options': [
                                    {'name': 'BBQ', 'price_modifier': 0},
                                    {'name': 'Ranch', 'price_modifier': 0},
                                    {'name': 'Mostaza Miel', 'price_modifier': 0},
                                    {'name': 'Buffalo', 'price_modifier': 0},
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Bebidas y Postres',
                'order': 3,
                'products': [
                    {
                        'name': 'Malteada',
                        'description': 'Malteada cremosa',
                        'price': 3.99,
                        'preparation_time': 5,
                        'option_groups': [
                            {
                                'name': 'Sabor',
                                'is_required': True,
                                'options': [
                                    {'name': 'Chocolate', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Vainilla', 'price_modifier': 0},
                                    {'name': 'Fresa', 'price_modifier': 0},
                                    {'name': 'Oreo', 'price_modifier': 0.50},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Coca Cola',
                        'description': 'Bebida gaseosa',
                        'price': 1.50,
                        'preparation_time': 2
                    }
                ]
            }
        ]

    def _get_ecuadorian_menu(self):
        return [
            {
                'name': 'Platos Típicos',
                'order': 1,
                'products': [
                    {
                        'name': 'Seco de Pollo',
                        'description': 'Pollo guisado con cerveza, arroz, maduro, ensalada y aguacate',
                        'price': 6.50,
                        'calories': 580,
                        'tags': ['popular', 'especial-casa'],
                        'preparation_time': 25,
                        'serving_size': '1 plato completo'
                    },
                    {
                        'name': 'Hornado',
                        'description': 'Cerdo hornado con mote, llapingachos, curtido y ají',
                        'price': 7.00,
                        'calories': 650,
                        'tags': ['chef-special'],
                        'preparation_time': 20
                    },
                    {
                        'name': 'Fritada',
                        'description': 'Fritada de cerdo con mote, tostado, maduro y ají',
                        'price': 6.50,
                        'calories': 620,
                        'tags': ['popular'],
                        'preparation_time': 20
                    },
                    {
                        'name': 'Guatita',
                        'description': 'Guatita criolla con arroz, maduro y aguacate',
                        'price': 5.50,
                        'calories': 480,
                        'preparation_time': 25
                    },
                    {
                        'name': 'Caldo de Gallina Criolla',
                        'description': 'Caldo de gallina con papa, yuca, arroz y aguacate',
                        'price': 6.00,
                        'calories': 420,
                        'tags': ['bajo-calorias'],
                        'preparation_time': 30
                    }
                ]
            },
            {
                'name': 'Desayunos',
                'order': 2,
                'products': [
                    {
                        'name': 'Bolón de Queso',
                        'description': 'Bolón de verde con queso, huevo frito y café',
                        'price': 4.00,
                        'calories': 380,
                        'tags': ['vegetariano'],
                        'preparation_time': 15
                    },
                    {
                        'name': 'Tigrillo',
                        'description': 'Verde con huevo, queso y café',
                        'price': 4.50,
                        'calories': 420,
                        'preparation_time': 18
                    }
                ]
            },
            {
                'name': 'Bebidas',
                'order': 3,
                'products': [
                    {
                        'name': 'Jugo Natural',
                        'description': 'Jugo de frutas naturales',
                        'price': 2.00,
                        'preparation_time': 5,
                        'option_groups': [
                            {
                                'name': 'Fruta',
                                'is_required': True,
                                'options': [
                                    {'name': 'Naranja', 'price_modifier': 0},
                                    {'name': 'Mora', 'price_modifier': 0},
                                    {'name': 'Naranjilla', 'price_modifier': 0},
                                    {'name': 'Tomate de árbol', 'price_modifier': 0},
                                    {'name': 'Maracuyá', 'price_modifier': 0.25},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Colada Morada',
                        'description': 'Colada tradicional ecuatoriana',
                        'price': 2.50,
                        'preparation_time': 5,
                        'tags': ['nuevo']
                    }
                ]
            }
        ]

    def _get_sushi_menu(self):
        return [
            {
                'name': 'Rolls Clásicos',
                'order': 1,
                'products': [
                    {
                        'name': 'California Roll',
                        'description': 'Cangrejo, aguacate, pepino y masago (8 piezas)',
                        'price': 8.99,
                        'calories': 280,
                        'tags': ['popular'],
                        'preparation_time': 15,
                        'serving_size': '8 piezas'
                    },
                    {
                        'name': 'Philadelphia Roll',
                        'description': 'Salmón, queso crema y aguacate (8 piezas)',
                        'price': 9.99,
                        'calories': 320,
                        'tags': ['chef-special'],
                        'preparation_time': 15
                    },
                    {
                        'name': 'Spicy Tuna Roll',
                        'description': 'Atún picante, pepino y salsa sriracha (8 piezas)',
                        'price': 10.99,
                        'calories': 290,
                        'tags': ['picante'],
                        'preparation_time': 15
                    }
                ]
            },
            {
                'name': 'Rolls Especiales',
                'order': 2,
                'products': [
                    {
                        'name': 'Dragon Roll',
                        'description': 'Camarón tempura, aguacate, anguila y salsa especial (10 piezas)',
                        'price': 14.99,
                        'compare_price': 16.99,
                        'calories': 380,
                        'tags': ['especial-casa', 'popular'],
                        'preparation_time': 20
                    },
                    {
                        'name': 'Rainbow Roll',
                        'description': 'California roll cubierto con salmón, atún y aguacate (10 piezas)',
                        'price': 15.99,
                        'calories': 350,
                        'tags': ['chef-special'],
                        'preparation_time': 20
                    }
                ]
            },
            {
                'name': 'Nigiri y Sashimi',
                'order': 3,
                'products': [
                    {
                        'name': 'Nigiri de Salmón',
                        'description': 'Nigiri de salmón fresco (2 piezas)',
                        'price': 5.99,
                        'calories': 140,
                        'preparation_time': 10
                    },
                    {
                        'name': 'Sashimi Mixto',
                        'description': 'Selección de sashimi: salmón, atún y pez blanco (9 piezas)',
                        'price': 16.99,
                        'calories': 200,
                        'tags': ['bajo-calorias'],
                        'preparation_time': 15
                    }
                ]
            }
        ]

    def _get_grill_menu(self):
        return [
            {
                'name': 'Carnes a la Parrilla',
                'order': 1,
                'products': [
                    {
                        'name': 'Churrasco',
                        'description': 'Lomo fino a la parrilla con chimichurri, papas fritas, arroz y ensalada',
                        'price': 12.99,
                        'calories': 680,
                        'tags': ['popular', 'chef-special'],
                        'preparation_time': 25,
                        'option_groups': [
                            {
                                'name': 'Término de la Carne',
                                'is_required': True,
                                'options': [
                                    {'name': 'Jugoso', 'price_modifier': 0},
                                    {'name': 'Término Medio', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Tres Cuartos', 'price_modifier': 0},
                                    {'name': 'Bien Cocido', 'price_modifier': 0},
                                ]
                            }
                        ],
                        'extras': [
                            {'name': 'Huevo Frito', 'price': 1.00},
                            {'name': 'Aguacate', 'price': 1.50},
                        ]
                    },
                    {
                        'name': 'Costillas BBQ',
                        'description': 'Costillas de cerdo glaseadas con salsa BBQ, papas y ensalada',
                        'price': 14.99,
                        'calories': 750,
                        'tags': ['especial-casa'],
                        'preparation_time': 30
                    },
                    {
                        'name': 'Pechuga a la Plancha',
                        'description': 'Pechuga de pollo a la plancha con vegetales y arroz',
                        'price': 9.99,
                        'calories': 420,
                        'tags': ['bajo-calorias'],
                        'preparation_time': 20
                    }
                ]
            },
            {
                'name': 'Parrilladas',
                'order': 2,
                'products': [
                    {
                        'name': 'Parrillada para 2',
                        'description': 'Churrasco, chorizo, morcilla, pollo, papas, maduro y chimichurri',
                        'price': 24.99,
                        'compare_price': 28.99,
                        'calories': 1200,
                        'tags': ['popular'],
                        'preparation_time': 35,
                        'serving_size': '2 personas'
                    },
                    {
                        'name': 'Parrillada Familiar',
                        'description': 'Parrillada completa para 4 personas',
                        'price': 45.99,
                        'calories': 2400,
                        'preparation_time': 40,
                        'serving_size': '4 personas'
                    }
                ]
            }
        ]

    def _get_chicken_menu(self):
        return [
            {
                'name': 'Pollos Completos',
                'order': 1,
                'products': [
                    {
                        'name': 'Pollo Entero',
                        'description': 'Pollo asado al carbón con papas, ensalada y ají de la casa',
                        'price': 12.00,
                        'calories': 1800,
                        'tags': ['popular'],
                        'preparation_time': 35,
                        'serving_size': '3-4 personas',
                        'extras': [
                            {'name': 'Papas Extra', 'price': 2.00},
                            {'name': 'Ensalada Extra', 'price': 1.50},
                            {'name': 'Ají Extra', 'price': 0.50},
                        ]
                    },
                    {
                        'name': 'Medio Pollo',
                        'description': 'Medio pollo asado con papas, ensalada y ají',
                        'price': 6.50,
                        'calories': 900,
                        'preparation_time': 30,
                        'serving_size': '2 personas'
                    }
                ]
            },
            {
                'name': 'Porciones',
                'order': 2,
                'products': [
                    {
                        'name': 'Cuarto de Pollo',
                        'description': 'Cuarto de pollo con papas y ensalada',
                        'price': 4.50,
                        'calories': 450,
                        'preparation_time': 25,
                        'option_groups': [
                            {
                                'name': 'Parte',
                                'is_required': True,
                                'options': [
                                    {'name': 'Pechuga', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Pierna', 'price_modifier': 0},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Alitas BBQ',
                        'description': '10 alitas bañadas en salsa BBQ con papas',
                        'price': 8.99,
                        'calories': 620,
                        'tags': ['popular'],
                        'preparation_time': 20
                    }
                ]
            },
            {
                'name': 'Bebidas',
                'order': 3,
                'products': [
                    {
                        'name': 'Gaseosa 2L',
                        'description': 'Gaseosa familiar',
                        'price': 2.50,
                        'preparation_time': 2
                    }
                ]
            }
        ]

    def _get_seafood_menu(self):
        return [
            {
                'name': 'Ceviches',
                'order': 1,
                'products': [
                    {
                        'name': 'Ceviche de Camarón',
                        'description': 'Camarón fresco con limón, cebolla, tomate y cilantro',
                        'price': 10.99,
                        'calories': 280,
                        'tags': ['popular', 'bajo-calorias'],
                        'preparation_time': 15
                    },
                    {
                        'name': 'Ceviche Mixto',
                        'description': 'Camarón, calamar, pescado y concha con limón',
                        'price': 12.99,
                        'calories': 320,
                        'tags': ['chef-special'],
                        'preparation_time': 18
                    },
                    {
                        'name': 'Ceviche de Pescado',
                        'description': 'Pescado fresco marinado en limón con cebolla y cilantro',
                        'price': 9.99,
                        'calories': 250,
                        'preparation_time': 15
                    }
                ]
            },
            {
                'name': 'Encocados',
                'order': 2,
                'products': [
                    {
                        'name': 'Encocado de Camarón',
                        'description': 'Camarones en salsa de coco con arroz y patacón',
                        'price': 13.99,
                        'calories': 580,
                        'tags': ['especial-casa'],
                        'preparation_time': 25
                    },
                    {
                        'name': 'Encocado Mixto',
                        'description': 'Mariscos variados en salsa de coco',
                        'price': 15.99,
                        'calories': 620,
                        'preparation_time': 28
                    }
                ]
            },
            {
                'name': 'Arroces Marineros',
                'order': 3,
                'products': [
                    {
                        'name': 'Arroz Marinero',
                        'description': 'Arroz con mariscos mixtos y salsa especial',
                        'price': 14.99,
                        'calories': 680,
                        'tags': ['popular'],
                        'preparation_time': 30
                    }
                ]
            }
        ]

    def _get_coffee_menu(self):
        return [
            {
                'name': 'Cafés Calientes',
                'order': 1,
                'products': [
                    {
                        'name': 'Cappuccino',
                        'description': 'Espresso con leche vaporizada y espuma',
                        'price': 3.50,
                        'calories': 120,
                        'tags': ['popular'],
                        'preparation_time': 5,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Pequeño (8oz)', 'price_modifier': -0.50},
                                    {'name': 'Mediano (12oz)', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Grande (16oz)', 'price_modifier': 0.75},
                                ]
                            },
                            {
                                'name': 'Tipo de Leche',
                                'is_required': True,
                                'options': [
                                    {'name': 'Leche Entera', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Leche Descremada', 'price_modifier': 0},
                                    {'name': 'Leche de Almendras', 'price_modifier': 0.50},
                                    {'name': 'Leche de Soya', 'price_modifier': 0.50},
                                ]
                            }
                        ],
                        'extras': [
                            {'name': 'Shot Extra de Espresso', 'price': 0.75},
                            {'name': 'Vainilla', 'price': 0.50},
                            {'name': 'Caramelo', 'price': 0.50},
                            {'name': 'Crema Batida', 'price': 0.75},
                        ]
                    },
                    {
                        'name': 'Latte',
                        'description': 'Espresso con leche vaporizada',
                        'price': 3.75,
                        'calories': 150,
                        'preparation_time': 5,
                        'option_groups': [
                            {
                                'name': 'Tamaño',
                                'is_required': True,
                                'options': [
                                    {'name': 'Pequeño (8oz)', 'price_modifier': -0.50},
                                    {'name': 'Mediano (12oz)', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Grande (16oz)', 'price_modifier': 0.75},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Americano',
                        'description': 'Espresso con agua caliente',
                        'price': 2.50,
                        'calories': 10,
                        'tags': ['bajo-calorias'],
                        'preparation_time': 3
                    }
                ]
            },
            {
                'name': 'Bebidas Frías',
                'order': 2,
                'products': [
                    {
                        'name': 'Frappuccino',
                        'description': 'Bebida helada con café, leche y hielo',
                        'price': 4.50,
                        'calories': 280,
                        'tags': ['popular'],
                        'preparation_time': 7,
                        'option_groups': [
                            {
                                'name': 'Sabor',
                                'is_required': True,
                                'options': [
                                    {'name': 'Café', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Caramelo', 'price_modifier': 0.50},
                                    {'name': 'Mocha', 'price_modifier': 0.50},
                                    {'name': 'Vainilla', 'price_modifier': 0.50},
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Desayunos',
                'order': 3,
                'products': [
                    {
                        'name': 'Croissant de Jamón y Queso',
                        'description': 'Croissant artesanal con jamón y queso',
                        'price': 4.00,
                        'calories': 380,
                        'preparation_time': 5
                    },
                    {
                        'name': 'Sandwich de Huevo y Tocino',
                        'description': 'Pan ciabatta con huevo revuelto, tocino y queso',
                        'price': 5.50,
                        'calories': 420,
                        'preparation_time': 8
                    }
                ]
            },
            {
                'name': 'Postres',
                'order': 4,
                'products': [
                    {
                        'name': 'Brownie de Chocolate',
                        'description': 'Brownie casero con nueces',
                        'price': 3.00,
                        'calories': 450,
                        'tags': ['nueces'],
                        'preparation_time': 3
                    },
                    {
                        'name': 'Cheesecake',
                        'description': 'Rebanada de cheesecake',
                        'price': 3.50,
                        'calories': 380,
                        'tags': ['lacteos'],
                        'preparation_time': 3,
                        'option_groups': [
                            {
                                'name': 'Sabor',
                                'is_required': True,
                                'options': [
                                    {'name': 'Natural', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Fresa', 'price_modifier': 0.50},
                                    {'name': 'Arequipe', 'price_modifier': 0.50},
                                ]
                            }
                        ]
                    }
                ]
            }
        ]

    def _get_mexican_menu(self):
        return [
            {
                'name': 'Tacos',
                'order': 1,
                'products': [
                    {
                        'name': 'Tacos al Pastor',
                        'description': 'Carne de cerdo marinada con piña, cebolla y cilantro (3 unidades)',
                        'price': 7.99,
                        'calories': 420,
                        'tags': ['popular', 'chef-special'],
                        'preparation_time': 15,
                        'serving_size': '3 tacos'
                    },
                    {
                        'name': 'Tacos de Carne Asada',
                        'description': 'Carne asada con guacamole y pico de gallo (3 unidades)',
                        'price': 8.99,
                        'calories': 450,
                        'preparation_time': 15
                    },
                    {
                        'name': 'Tacos de Pollo',
                        'description': 'Pollo marinado con salsa verde (3 unidades)',
                        'price': 6.99,
                        'calories': 380,
                        'preparation_time': 12
                    }
                ]
            },
            {
                'name': 'Burritos',
                'order': 2,
                'products': [
                    {
                        'name': 'Burrito Mexicano',
                        'description': 'Carne, frijoles, arroz, queso, guacamole y crema',
                        'price': 9.99,
                        'calories': 680,
                        'tags': ['especial-casa'],
                        'preparation_time': 18,
                        'option_groups': [
                            {
                                'name': 'Proteína',
                                'is_required': True,
                                'options': [
                                    {'name': 'Carne Asada', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Pollo', 'price_modifier': 0},
                                    {'name': 'Pastor', 'price_modifier': 0.50},
                                    {'name': 'Vegetariano', 'price_modifier': -1.00},
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Quesadillas',
                'order': 3,
                'products': [
                    {
                        'name': 'Quesadilla de Queso',
                        'description': 'Tortilla con queso fundido',
                        'price': 5.99,
                        'calories': 480,
                        'tags': ['vegetariano'],
                        'preparation_time': 10
                    },
                    {
                        'name': 'Quesadilla Mixta',
                        'description': 'Tortilla con queso, carne y vegetales',
                        'price': 8.99,
                        'calories': 620,
                        'preparation_time': 15
                    }
                ]
            },
            {
                'name': 'Acompañamientos',
                'order': 4,
                'products': [
                    {
                        'name': 'Guacamole con Chips',
                        'description': 'Guacamole fresco con totopos',
                        'price': 4.99,
                        'calories': 320,
                        'tags': ['vegetariano', 'vegano'],
                        'preparation_time': 5
                    },
                    {
                        'name': 'Nachos Supremos',
                        'description': 'Nachos con queso, carne, guacamole y crema',
                        'price': 7.99,
                        'calories': 680,
                        'preparation_time': 12
                    }
                ]
            }
        ]

    def _get_healthy_menu(self):
        return [
            {
                'name': 'Bowls Saludables',
                'order': 1,
                'products': [
                    {
                        'name': 'Buddha Bowl',
                        'description': 'Quinoa, garbanzos, aguacate, zanahoria, brócoli y tahini',
                        'price': 9.99,
                        'calories': 420,
                        'tags': ['vegano', 'sin-gluten', 'bajo-calorias'],
                        'preparation_time': 15
                    },
                    {
                        'name': 'Protein Bowl',
                        'description': 'Pollo a la plancha, arroz integral, vegetales y huevo',
                        'price': 10.99,
                        'calories': 480,
                        'tags': ['sin-gluten', 'bajo-calorias'],
                        'preparation_time': 18
                    },
                    {
                        'name': 'Poke Bowl',
                        'description': 'Salmón, arroz, edamame, aguacate y salsa ponzu',
                        'price': 12.99,
                        'calories': 520,
                        'tags': ['sin-gluten'],
                        'preparation_time': 15
                    }
                ]
            },
            {
                'name': 'Ensaladas',
                'order': 2,
                'products': [
                    {
                        'name': 'Ensalada César',
                        'description': 'Lechuga romana, pollo, parmesano, crutones y aderezo césar',
                        'price': 8.99,
                        'calories': 380,
                        'preparation_time': 10
                    },
                    {
                        'name': 'Ensalada Griega',
                        'description': 'Tomate, pepino, cebolla, aceitunas, queso feta y aceite de oliva',
                        'price': 7.99,
                        'calories': 280,
                        'tags': ['vegetariano', 'sin-gluten'],
                        'preparation_time': 8
                    }
                ]
            },
            {
                'name': 'Smoothies',
                'order': 3,
                'products': [
                    {
                        'name': 'Green Smoothie',
                        'description': 'Espinaca, piña, manzana verde, jengibre y limón',
                        'price': 5.99,
                        'calories': 180,
                        'tags': ['vegano', 'bajo-calorias'],
                        'preparation_time': 5
                    },
                    {
                        'name': 'Berry Protein Smoothie',
                        'description': 'Frutos rojos, plátano, proteína whey y leche de almendras',
                        'price': 6.99,
                        'calories': 280,
                        'preparation_time': 5
                    }
                ]
            }
        ]

    def _get_breakfast_menu(self):
        return [
            {
                'name': 'Desayunos Tradicionales',
                'order': 1,
                'products': [
                    {
                        'name': 'Desayuno Completo',
                        'description': 'Huevos al gusto, pan, café, jugo de naranja, queso y mermelada',
                        'price': 5.50,
                        'calories': 520,
                        'tags': ['popular'],
                        'preparation_time': 15,
                        'option_groups': [
                            {
                                'name': 'Tipo de Huevos',
                                'is_required': True,
                                'options': [
                                    {'name': 'Fritos', 'price_modifier': 0, 'is_default': True},
                                    {'name': 'Revueltos', 'price_modifier': 0},
                                    {'name': 'Pericos', 'price_modifier': 0.50},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Bolón Mixto',
                        'description': 'Bolón de verde con queso y chicharrón, café o jugo',
                        'price': 4.50,
                        'calories': 480,
                        'tags': ['especial-casa'],
                        'preparation_time': 12
                    },
                    {
                        'name': 'Tigrillo',
                        'description': 'Verde maduro con huevo y queso, café',
                        'price': 4.00,
                        'calories': 420,
                        'preparation_time': 15
                    },
                    {
                        'name': 'Empanadas de Morocho',
                        'description': '3 empanadas con café o colada (queso, viento o carne)',
                        'price': 3.50,
                        'calories': 380,
                        'preparation_time': 10
                    }
                ]
            },
            {
                'name': 'Panes y Tostadas',
                'order': 2,
                'products': [
                    {
                        'name': 'Tostadas Francesas',
                        'description': 'Pan francés con miel, mantequilla y fruta',
                        'price': 4.99,
                        'calories': 420,
                        'preparation_time': 12
                    },
                    {
                        'name': 'Pan con Mantequilla y Mermelada',
                        'description': 'Pan fresco con mantequilla, mermelada y café',
                        'price': 2.50,
                        'calories': 280,
                        'preparation_time': 5
                    }
                ]
            },
            {
                'name': 'Bebidas',
                'order': 3,
                'products': [
                    {
                        'name': 'Café con Leche',
                        'description': 'Café con leche caliente',
                        'price': 1.50,
                        'preparation_time': 3
                    },
                    {
                        'name': 'Jugo de Naranja',
                        'description': 'Jugo de naranja natural',
                        'price': 2.00,
                        'preparation_time': 5
                    },
                    {
                        'name': 'Avena Caliente',
                        'description': 'Avena con canela y pasas',
                        'price': 2.50,
                        'calories': 220,
                        'preparation_time': 8
                    }
                ]
            }
        ]

    def _get_bakery_menu(self):
        return [
            {
                'name': 'Panes Artesanales',
                'order': 1,
                'products': [
                    {
                        'name': 'Baguette Francesa',
                        'description': 'Baguette tradicional francesa crujiente',
                        'price': 2.50,
                        'calories': 280,
                        'preparation_time': 5
                    },
                    {
                        'name': 'Pan Integral',
                        'description': 'Pan de granos enteros',
                        'price': 3.00,
                        'calories': 240,
                        'tags': ['bajo-calorias'],
                        'preparation_time': 5
                    },
                    {
                        'name': 'Croissant de Mantequilla',
                        'description': 'Croissant francés hojaldrado',
                        'price': 2.00,
                        'calories': 320,
                        'tags': ['popular'],
                        'preparation_time': 3
                    }
                ]
            },
            {
                'name': 'Repostería',
                'order': 2,
                'products': [
                    {
                        'name': 'Pastel de Chocolate',
                        'description': 'Rebanada de pastel de chocolate con ganache',
                        'price': 4.50,
                        'calories': 480,
                        'tags': ['lacteos', 'popular'],
                        'preparation_time': 5
                    },
                    {
                        'name': 'Torta de Zanahoria',
                        'description': 'Torta casera de zanahoria con frosting de queso crema',
                        'price': 4.00,
                        'calories': 420,
                        'tags': ['lacteos'],
                        'preparation_time': 5
                    },
                    {
                        'name': 'Macaron Francés',
                        'description': 'Macaron de almendra (2 unidades)',
                        'price': 3.50,
                        'calories': 180,
                        'tags': ['nueces'],
                        'preparation_time': 3,
                        'option_groups': [
                            {
                                'name': 'Sabor',
                                'is_required': True,
                                'options': [
                                    {'name': 'Frambuesa', 'price_modifier': 0},
                                    {'name': 'Chocolate', 'price_modifier': 0},
                                    {'name': 'Vainilla', 'price_modifier': 0},
                                    {'name': 'Pistacho', 'price_modifier': 0.50},
                                ]
                            }
                        ]
                    },
                    {
                        'name': 'Donas Glaseadas',
                        'description': 'Donas con diferentes coberturas (3 unidades)',
                        'price': 5.00,
                        'calories': 540,
                        'preparation_time': 5
                    }
                ]
            },
            {
                'name': 'Galletas',
                'order': 3,
                'products': [
                    {
                        'name': 'Galletas de Chocolate Chip',
                        'description': 'Galletas con chispas de chocolate (6 unidades)',
                        'price': 3.50,
                        'calories': 420,
                        'preparation_time': 3
                    },
                    {
                        'name': 'Galletas de Avena',
                        'description': 'Galletas de avena con pasas (6 unidades)',
                        'price': 3.00,
                        'calories': 360,
                        'preparation_time': 3
                    }
                ]
            }
        ]