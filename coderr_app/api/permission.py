from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsOfferOwner(BasePermission):

    """
    Permission class that allows access only to the owner of an offer.

    This permission ensures that only the user who created the offer
    (stored in `obj.user`) is allowed to update or delete it. It is
    typically used in RetrieveUpdateDestroyAPIView or UpdateAPIView
    for offer modification endpoints.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check whether the requesting user is the owner of the offer.

        Args:
            request (Request): The incoming HTTP request.
            view (APIView): The view where the permission is applied.
            obj (Offer): The offer instance being accessed.

        Returns:
            bool: True if the user owns the offer, otherwise False.
        """
        return obj.user == request.user
    


class IsOrderOwner(BasePermission):

    """
    Permission class that allows access only to users involved in an order.

    This permission ensures that only the customer who placed the order
    or the business user who is fulfilling the order can view, update,
    or delete the order. It is typically used in detail views where
    object-level permission checks are required.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check whether the requesting user is either the customer or the business user.

        Args:
            request (Request): The incoming HTTP request.
            view (APIView): The view where the permission is applied.
            obj (Order): The order instance being accessed.

        Returns:
            bool: True if the user is involved in the order, otherwise False.
        """ 
        return obj.customer_user == request.user or obj.business_user == request.user
    


class IsCustomerUser(BasePermission):

    """
    Permission class that allows access only to authenticated customer users.

    This permission ensures that the requesting user is logged in and that
    their profile type is set to 'customer'. It is typically used for views
    where only customer accounts should have access (e.g., placing orders).
    """

    def has_permission(self, request, view):
        """
        Check whether the requesting user is authenticated and a customer.

        Args:
            request (Request): The incoming HTTP request.
            view (APIView): The view where the permission is applied.

        Returns:
            bool: True if the user is authenticated and has type 'customer'.
        """
        user = request.user

        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'type', None) == 'customer'
    

class IsOrderParticipant(BasePermission):
    """
    Permission class that allows access only to authenticated users
    who are either customers or business users.

    This ensures that only valid platform participants can interact
    with order-related endpoints, while blocking unauthorized or
    unauthenticated users.
    """
    
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'type', None) in ['customer', 'business']



class IsCustomerReviewerorReadOnly(BasePermission):

    """
    Permission class that allows:
    - Read-only access for everyone (GET, HEAD, OPTIONS)
    - POST access only for authenticated customer users
    - Update/delete access only for the original reviewer

    This ensures that only customers can create reviews and only the
    review author can modify or delete their own review.
    """

    def has_permission(self, request, view):
        """
        Global permission check before accessing the view.

        Returns:
            True for safe methods.
            True for POST only if the user is a customer.
            False for unauthenticated users.
        """
        user = request.user

        if not user or not user.is_authenticated:
            return False
        
        if request.method in SAFE_METHODS:
            return True
        
        if request.method == 'POST':
            return getattr(user, 'type', None) == 'customer'

        return True
    

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.

        Allows:
            - Read-only access for everyone
            - Write access only for the user who wrote the review
        """
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer == request.user
    


class IsReviewerOwner(BasePermission):

    """
    Permission class that allows only the original reviewer to modify or delete a review.

    Read-only access (GET, HEAD, OPTIONS) is allowed for everyone.
    Write access (PUT, PATCH, DELETE) is restricted to the user who created the review.
    """

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check.

        Allows:
            - Read-only access for all users
            - Write access only for the review's author
        """
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer == request.user
    


