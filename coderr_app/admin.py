from django.contrib import admin


from .models import Offer, OfferDetail, Order, Review, BaseInfo

"""
Admin configuration for the Coderr application.

This file registers all core models (Offer, OfferDetail, Order, Review, BaseInfo)
so they can be managed through the Django admin interface. Additional admin
customization can be added to improve list display, filtering, and search.
"""

admin.site.register(Offer)
"""
Admin configuration for the Offer model.
"""

admin.site.register(OfferDetail)
"""
Admin configuration for the OfferDetail model.
"""

admin.site.register(Order)
"""
Admin configuration for the Order model.
"""

admin.site.register(Review)
"""
Admin configuration for the Review model.
"""
