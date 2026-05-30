from django.db import models

from auth_app.models import Profile



class Offer(models.Model):

    """
    Represents a service offer created by a business profile.

    Each offer contains basic information such as title, description,
    minimum price, and minimum delivery time. Offers belong to a specific
    user (Profile) and may include an optional image. Timestamps track
    creation and updates for sorting and display purposes.

    Fields:
        user (ForeignKey): The profile that created the offer.
        title (str): The title of the offer.
        image (ImageField): Optional image representing the offer.
        description (str): Optional detailed description.
        min_price (Decimal): Minimum price for the offer.
        min_delivery_time (int): Minimum delivery time in days.
        created_at (datetime): Timestamp when the offer was created.
        updated_at (datetime): Timestamp when the offer was last updated.
    """
        
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='offers/', null=True, blank=True)
    description = models.TextField(blank=True) 
    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_delivery_time = models.PositiveIntegerField(help_text='Minimum delivery time in days', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title



class OfferDetail(models.Model):

    """
    Represents a specific tier or package within an offer.

    Each Offer can contain multiple OfferDetail entries, such as
    'Basic', 'Standard', or 'Premium'. These detail records define
    pricing, delivery time, included features, and revision limits
    for each package level.

    Fields:
        offer (ForeignKey): The parent Offer this detail belongs to.
        title (str): The name of the package (e.g., "Basic Package").
        description (str): Optional description of what the package includes.
        price (Decimal): The price of this package.
        delivery_time_in_days (int): Estimated delivery time for this package.
        revisions (int): Number of revisions included.
        features (list): JSON list of features included in the package.
        offer_type (str): One of: basic, standard, premium.
    """
        
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time_in_days = models.PositiveIntegerField(help_text='Delivery time in days')
    revisions = models.PositiveIntegerField(default=0)
    features = models.JSONField(default=list, blank=True) 
    offer_type = models.CharField(max_length=50, choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')], default='basic')


    def __str__(self):
        return f'{self.offer.title} - {self.title}'
    


class Order(models.Model):

    """
    Represents an order placed by a customer for a specific offer package.

    Each order links a customer and a business user, includes pricing,
    delivery time, selected offer type (basic/standard/premium), and
    tracks the order's lifecycle through various status stages.

    Fields:
        customer_user (ForeignKey): The profile of the customer placing the order.
        business_user (ForeignKey): The profile of the business fulfilling the order.
        title (str): Title of the ordered service.
        revisions (int): Number of revisions included in the order.
        delivery_time_in_days (int): Estimated delivery time.
        price (Decimal): Final price of the order.
        features (list): JSON list of included features.
        offer_type (str): One of: basic, standard, premium.
        status (str): Order status (pending, in_progress, completed, cancelled).
        created_at (datetime): Timestamp when the order was created.
        updated_at (datetime): Timestamp when the order was last updated.
        order_count (int): Internal counter for total orders (optional usage).
        completed_order_count (int): Internal counter for completed orders.
    """

    STATUS_CHOICES = [('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]
    customer_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='customer_orders')
    business_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='business_orders')

    title = models.CharField(max_length=200)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField()
    price =  models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, blank=True)
    offer_type = models.CharField(max_length=50, choices=[('basic', 'Basic'), ('standard', 'Standard'), ('premium', 'Premium')], default='basic')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    order_count = models.PositiveIntegerField(default=0)
    completed_order_count = models.PositiveIntegerField(default=0)  


    def __str__(self):
        return f'Order {self.id}'



class Review(models.Model):

    """
    Represents a customer review left for a business user.

    Each review links a reviewer (customer) to a business user and contains
    a numeric rating along with an optional text description. Timestamps
    track when the review was created and last updated.

    Fields:
        business_user (ForeignKey): The profile receiving the review.
        reviewer (ForeignKey): The profile writing the review.
        rating (int): Rating value (typically 1–5).
        description (str): Optional written feedback.
        created_at (datetime): Timestamp when the review was created.
        updated_at (datetime): Timestamp when the review was last updated.
    """

    business_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='written_reviews')
    rating = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.reviewer.user.username} {self.business_user.user.username}'

    

class BaseInfo(models.Model):

    """
    Represents a single review entry used for platform-wide statistics.

    This model stores a rating and optional comment for a specific offer
    written by a specific user. It is used to calculate aggregated metrics
    such as total review count and average rating across the platform.

    Fields:
        user (ForeignKey): The profile that wrote the review.
        offer (ForeignKey): The offer being reviewed.
        rating (Decimal): Rating value (e.g., 4.5).
        comment (str): Optional text feedback.
        created_at (datetime): Timestamp when the review was created.
    """
        
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='reviews')
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Review for {self.offer.title} by {self.user.user.username}'


