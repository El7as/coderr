from django.contrib.auth.models import AbstractUser
from django.db import models




class Profile(AbstractUser):

    """
    Extended user model for the Coderr platform.

    This model inherits from Django's AbstractUser and adds additional
    fields required for both customer and business accounts.

    Fields:
        USER_TYPES (list):
            Defines the two possible user roles:
            - 'customer': Regular users who can create reviews and place orders.
            - 'business': Service providers who can create offers.

        file (ImageField):
            Optional profile image uploaded by the user.
            Stored under the 'profiles/' directory.

        location (CharField):
            Optional text field representing the user's city or region.

        tel (CharField):
            Optional phone number for contact purposes.

        description (TextField):
            Optional profile description or business bio.

        working_hours (CharField):
            Optional field used mainly by business users to indicate availability.

        type (CharField):
            Defines whether the user is a 'customer' or 'business'.
            Defaults to 'customer'.

        created_at (DateTimeField):
            Automatically stores the timestamp when the profile is created.

    Methods:
        __str__():
            Returns a readable representation of the user, including
            their username and user type.
    """

    USER_TYPES = [('customer', 'Customer'), ('business', 'Business')]

   
    file = models.ImageField(upload_to='profiles/', null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    tel = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.username} ({self.type})'
    
