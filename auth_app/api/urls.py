from django.urls import path


from .views import RegistrationView, LoginView, ProfileDetailView, BusinessProfilListView, CustomerProfilListView

"""
URL configuration for the authentication module.

This file defines all authentication-related API endpoints, including:
- User registration
- User login
- Profile retrieval and update
- Listing business and customer profiles

Each endpoint is mapped to its corresponding view class.
"""

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),

    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/business/', BusinessProfilListView.as_view(), name='business'),
    path('profiles/customer/', CustomerProfilListView.as_view(), name='customer'),
]
