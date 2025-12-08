# apps/products/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from decimal import Decimal


class Category(models.Model):
    """Categorías del Menú (Ej: Pizzas, Bebidas, Postres)"""
    
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='menu_categories',
        verbose_name='Restaurante'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre de la Categoría'
    )
    
    slug = models.SlugField(
        max_length=120,
        blank=True,
        verbose_name='Slug'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name='Imagen'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden de Visualización',
        help_text='Orden en el menú (menor número = primero)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['restaurant', 'order', 'name']
        unique_together = ['restaurant', 'slug']
        indexes = [
            models.Index(fields=['restaurant', 'is_active']),
            models.Index(fields=['order']),
        ]
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductTag(models.Model):
    """Etiquetas para productos (Vegetariano, Picante, Sin Gluten, etc.)"""
    
    class TagType(models.TextChoices):
        DIETARY = 'DIETARY', 'Dietético'  # Vegetariano, Vegano, Sin Gluten
        SPICE = 'SPICE', 'Picante'  # Picante, Muy Picante
        SPECIAL = 'SPECIAL', 'Especial'  # Nuevo, Popular, Chef's Special
        ALLERGEN = 'ALLERGEN', 'Alérgeno'  # Contiene Nueces, Lácteos, etc.
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nombre'
    )
    
    slug = models.SlugField(
        max_length=60,
        unique=True,
        blank=True,
        verbose_name='Slug'
    )
    
    tag_type = models.CharField(
        max_length=20,
        choices=TagType.choices,
        default=TagType.SPECIAL,
        verbose_name='Tipo de Etiqueta'
    )
    
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Icono/Emoji',
        help_text='Ej: 🌱, 🌶️, ⭐'
    )
    
    color = models.CharField(
        max_length=7,
        default='#6B7280',
        verbose_name='Color Hex',
        help_text='Ej: #FF5733'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa'
    )
    
    class Meta:
        verbose_name = 'Etiqueta de Producto'
        verbose_name_plural = 'Etiquetas de Productos'
        ordering = ['tag_type', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name}" if self.icon else self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Producto/Item del Menú"""
    
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Restaurante'
    )
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Categoría'
    )
    
    # Información Básica
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Producto'
    )
    
    slug = models.SlugField(
        max_length=250,
        blank=True,
        verbose_name='Slug'
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada del producto'
    )
    
    short_description = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Descripción Corta',
        help_text='Para listados y vistas previas'
    )
    
    # Imágenes
    image = models.ImageField(
        upload_to='products/',
        verbose_name='Imagen Principal'
    )
    
    # Precios
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    compare_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Precio de Comparación',
        help_text='Precio original antes del descuento',
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Porcentaje de Descuento',
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))]
    )
    
    # Etiquetas
    tags = models.ManyToManyField(
        ProductTag,
        blank=True,
        related_name='products',
        verbose_name='Etiquetas'
    )
    
    # Disponibilidad y Stock
    is_available = models.BooleanField(
        default=True,
        verbose_name='Disponible'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está desactivado, no se muestra en el menú'
    )
    
    stock_quantity = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Cantidad en Stock',
        help_text='Dejar vacío para stock ilimitado'
    )
    
    track_inventory = models.BooleanField(
        default=False,
        verbose_name='Controlar Inventario'
    )
    
    # Tiempo de Preparación
    preparation_time = models.PositiveIntegerField(
        default=15,
        verbose_name='Tiempo de Preparación (min)',
        help_text='Tiempo estimado en minutos'
    )
    
    # Información Nutricional
    calories = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Calorías'
    )
    
    serving_size = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Tamaño de Porción',
        help_text='Ej: 250g, 1 unidad'
    )
    
    # Destacados y Promociones
    is_featured = models.BooleanField(
        default=False,
        verbose_name='Destacado',
        help_text='Aparece en la sección de destacados'
    )
    
    is_new = models.BooleanField(
        default=False,
        verbose_name='Nuevo',
        help_text='Muestra badge de "Nuevo"'
    )
    
    is_popular = models.BooleanField(
        default=False,
        verbose_name='Popular',
        help_text='Muestra badge de "Popular"'
    )
    
    # Estadísticas
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Vistas'
    )
    
    orders_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Veces Ordenado'
    )
    
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('5.00'),
        verbose_name='Calificación',
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('5'))]
    )
    
    reviews_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Número de Reseñas'
    )
    
    # Orden de visualización
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden',
        help_text='Orden dentro de la categoría'
    )
    
    # SEO
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Meta Title'
    )
    
    meta_description = models.TextField(
        blank=True,
        verbose_name='Meta Description'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['restaurant', 'category', 'order', 'name']
        unique_together = ['restaurant', 'slug']
        indexes = [
            models.Index(fields=['restaurant', 'is_active', 'is_available']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-orders_count']),
            models.Index(fields=['-rating']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Calcular porcentaje de descuento si hay compare_price
        if self.compare_price and self.compare_price > self.price:
            self.discount_percentage = ((self.compare_price - self.price) / self.compare_price) * 100
        else:
            self.discount_percentage = Decimal('0.00')
        
        super().save(*args, **kwargs)
    
    @property
    def is_in_stock(self):
        """Verifica si el producto tiene stock disponible"""
        if not self.track_inventory:
            return True
        return self.stock_quantity and self.stock_quantity > 0
    
    @property
    def has_discount(self):
        """Verifica si el producto tiene descuento"""
        return self.compare_price and self.compare_price > self.price
    
    @property
    def final_price(self):
        """Retorna el precio final del producto"""
        return self.price
    
    def reduce_stock(self, quantity=1):
        """Reduce el stock del producto"""
        if self.track_inventory and self.stock_quantity:
            self.stock_quantity -= quantity
            if self.stock_quantity <= 0:
                self.is_available = False
            self.save()
    
    def increase_stock(self, quantity=1):
        """Aumenta el stock del producto"""
        if self.track_inventory:
            if self.stock_quantity is None:
                self.stock_quantity = 0
            self.stock_quantity += quantity
            self.is_available = True
            self.save()


class ProductImage(models.Model):
    """Galería de imágenes adicionales del producto"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Producto'
    )
    
    image = models.ImageField(
        upload_to='products/gallery/',
        verbose_name='Imagen'
    )
    
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Texto Alternativo'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Subida'
    )
    
    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.product.name} - Imagen {self.id}"


class ProductExtra(models.Model):
    """Extras/Agregados del Producto (con costo adicional)"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='extras',
        verbose_name='Producto'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre del Extra'
    )
    
    description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Descripción'
    )
    
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Precio Adicional',
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    is_available = models.BooleanField(
        default=True,
        verbose_name='Disponible'
    )
    
    max_quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad Máxima',
        help_text='Cantidad máxima que se puede agregar'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    class Meta:
        verbose_name = 'Extra de Producto'
        verbose_name_plural = 'Extras de Productos'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} (+${self.price})"


class ProductOptionGroup(models.Model):
    """Grupo de Opciones (Ej: Tamaño, Tipo de Masa, etc.)"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='option_groups',
        verbose_name='Producto'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre del Grupo',
        help_text='Ej: Tamaño, Tipo de Masa'
    )
    
    is_required = models.BooleanField(
        default=False,
        verbose_name='Requerido',
        help_text='El cliente debe seleccionar una opción'
    )
    
    min_selections = models.PositiveIntegerField(
        default=1,
        verbose_name='Selecciones Mínimas'
    )
    
    max_selections = models.PositiveIntegerField(
        default=1,
        verbose_name='Selecciones Máximas',
        help_text='1 = selección única, >1 = selección múltiple'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    class Meta:
        verbose_name = 'Grupo de Opciones'
        verbose_name_plural = 'Grupos de Opciones'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductOption(models.Model):
    """Opciones individuales dentro de un grupo"""
    
    group = models.ForeignKey(
        ProductOptionGroup,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='Grupo'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre de la Opción'
    )
    
    price_modifier = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Modificador de Precio',
        help_text='Puede ser positivo (aumenta) o negativo (reduce)'
    )
    
    is_available = models.BooleanField(
        default=True,
        verbose_name='Disponible'
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name='Opción por Defecto',
        help_text='Viene preseleccionada'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    class Meta:
        verbose_name = 'Opción de Producto'
        verbose_name_plural = 'Opciones de Producto'
        ordering = ['order', 'name']
    
    def __str__(self):
        modifier = f" (+${self.price_modifier})" if self.price_modifier > 0 else f" (-${abs(self.price_modifier)})" if self.price_modifier < 0 else ""
        return f"{self.name}{modifier}"


class ProductReview(models.Model):
    """Reseñas específicas de productos"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Producto'
    )
    
    customer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='product_reviews',
        verbose_name='Cliente'
    )
    
    order_item = models.ForeignKey(
        'orders.OrderItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='product_reviews',
        verbose_name='Item del Pedido'
    )
    
    rating = models.IntegerField(
        verbose_name='Calificación',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Calificación de 1 a 5 estrellas'
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name='Comentario'
    )
    
    # Imágenes de la reseña
    image1 = models.ImageField(
        upload_to='reviews/products/',
        null=True,
        blank=True,
        verbose_name='Imagen 1'
    )
    
    image2 = models.ImageField(
        upload_to='reviews/products/',
        null=True,
        blank=True,
        verbose_name='Imagen 2'
    )
    
    image3 = models.ImageField(
        upload_to='reviews/products/',
        null=True,
        blank=True,
        verbose_name='Imagen 3'
    )
    
    # Estado
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Verificada',
        help_text='El cliente compró el producto'
    )
    
    is_visible = models.BooleanField(
        default=True,
        verbose_name='Visible'
    )
    
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Útil (conteo)',
        help_text='Cuántas personas marcaron como útil'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Reseña de Producto'
        verbose_name_plural = 'Reseñas de Productos'
        ordering = ['-created_at']
        unique_together = ['product', 'customer', 'order_item']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.product.name} ({self.rating}⭐)"
    
    def save(self, *args, **kwargs):
        """Actualiza el rating del producto al guardar"""
        super().save(*args, **kwargs)
        self.product.calculate_rating()


# Extensión del modelo Product para el método calculate_rating
def calculate_product_rating(self):
    """Recalcula el rating promedio del producto"""
    from django.db.models import Avg
    avg_rating = self.reviews.filter(is_visible=True).aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        self.rating = round(avg_rating, 2)
        self.reviews_count = self.reviews.filter(is_visible=True).count()
        self.save()

# Agregar el método al modelo Product
Product.calculate_rating = calculate_product_rating