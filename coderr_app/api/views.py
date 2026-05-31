from rest_framework import generics, filters, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError, NotAuthenticated

from django.db import models
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend


from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail, Review, Order

from .pagination import OfferPagination
from .permission import IsOfferOwner, IsOrderOwner, IsCustomerUser, IsCustomerReviewerorReadOnly, IsReviewerOwner, IsOrderParticipant
from .serializer import OfferSerializer, OfferPostSerializer, OfferDetailViewSerializer, OfferPatchSerializer, OfferdetailsSerializer,\
                        OrderSerializer, OrderCreateSerializer, ReviewSerializer



class OfferListView(generics.ListCreateAPIView):

    """
    Handles listing and creating Offer objects.

    GET:
        - Supports search, ordering, and filtering by:
            creator_id, min_price, max_price,
            min_delivery_time, max_delivery_time
        - Returns paginated OfferSerializer output.

    POST:
        - Only authenticated business users may create offers.
        - Requires at least 3 nested offer details.
        - Automatically calculates min_price and min_delivery_time.
    """
        
    queryset = Offer.objects.all()
    permission_classes = [AllowAny]
    pagination_class = OfferPagination

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'user__username']
    ordering_fields = ['updated_at', 'min_price', 'min_delivery_time']


    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OfferSerializer
        return OfferPostSerializer


    def validate_int(self, value, field_name):
        """
        Validates that a query parameter is an integer.
        """
        if value is None:
            return None
        try:
            value = int(value)
        except ValueError:
            raise ValidationError({field_name: f"{field_name} must be an integer."})
        return value


    def get_queryset(self):
        """
        Applies filtering for price, delivery time, and creator.
        """
        qs = super().get_queryset()
        params = self.request.query_params

        creator_id = self.validate_int(params.get('creator_id'), 'creator_id')
        min_price = self.validate_int(params.get('min_price'), 'min_price')
        max_price = self.validate_int(params.get('max_price'), 'max_price')
        min_delivery_time = self.validate_int(params.get('min_delivery_time'), 'min_delivery_time')
        max_delivery_time = self.validate_int(params.get('max_delivery_time'), 'max_delivery_time')

        for field, value in {"min_price": min_price, "max_price": max_price, "min_delivery_time": min_delivery_time, "max_delivery_time": max_delivery_time}.items():
            if value is not None and value < 0:
                raise ValidationError({field: f"{field} must be >= 0."})

        if creator_id is not None:
            qs = qs.filter(user__id=creator_id)
        if min_price is not None:
            qs = qs.filter(min_price__gte=min_price)
        if max_price is not None:
            qs = qs.filter(min_price__lte=max_price)
        if min_delivery_time is not None:
            qs = qs.filter(min_delivery_time__gte=min_delivery_time)
        if max_delivery_time is not None:
            qs = qs.filter(min_delivery_time__lte=max_delivery_time)

        return qs
    

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            errors = exc.detail
            normalized = {}

            for field, value in errors.items():
                if isinstance(value, list) and len(value) == 1:
                    normalized[field] = value[0]
                else:
                    normalized[field] = value

            return Response(normalized, status=400)
        
        self.perform_create(serializer)
        return Response(self.response.data, status=201)


    def perform_create(self, serializer):
        """
        Creates an offer and calculates min_price and min_delivery_time.
        """
        user = self.request.user

        if not user or not user.is_authenticated:
            raise NotAuthenticated('Authentication credentials were not provided.')

        if getattr(user, 'type', None) != 'business':
            raise PermissionDenied('Only business users can create offers.')

        offer = serializer.save()
        details_data = self.request.data.get('details', [])
        if len(details_data) < 3:
            raise ValidationError('At least 3 offer details are required.')

        offer.min_price = min(d['price'] for d in details_data)
        offer.min_delivery_time = min(d['delivery_time_in_days'] for d in details_data)
        offer.save()



class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):

    """
    Handles retrieving, updating, and deleting a single Offer object.

    GET:
        - Returns full offer details including nested OfferDetail links.

    PATCH / PUT:
        - Only the offer owner may update.
        - Uses OfferPatchSerializer for partial updates.
        - Rejects empty request bodies.

    DELETE:
        - Only the offer owner may delete the offer.
    """
        
    queryset = Offer.objects.all()


    def get_permissions(self):
        """
        Dynamically assign permissions based on request method.
        """
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOfferOwner()]


    def get_serializer_class(self):
        """
        Selects the appropriate serializer based on request method.
        """
        if self.request.method in ['PATCH', 'PUT']:
            return OfferPatchSerializer
        return OfferDetailViewSerializer
    

    def update(self, request, *args, **kwargs):
        """
        Custom update method to enforce non-empty request bodies.
        """
        if not request.data:
            return Response({"error": "Body must not be empty."},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(self.get_object(), data= request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)



class OfferDetailItemView(generics.RetrieveAPIView):

    """
    Retrieves a single OfferDetail object.

    This endpoint is used when the client needs the full detail of a
    specific offer package (Basic, Standard, Premium). It returns the
    complete detail record including price, delivery time, revisions,
    features, and offer type.

    Only authenticated users may access this endpoint.
    """
        
    queryset = OfferDetail.objects.all()
    serializer_class = OfferdetailsSerializer
    permission_classes = [IsAuthenticated]



class OrderListView(generics.ListCreateAPIView):
      
    """
    Handles listing and creating Order objects.

    GET:
        - Returns all orders where the authenticated user is either
          the customer or the business user.

    POST:
        - Creates a new order from a selected OfferDetail.
        - Validates that the offer_detail_id exists.
        - Copies all relevant fields (title, price, revisions, etc.)
          from the OfferDetail into the new Order.
    """
      
    pagination_class = None


    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsCustomerUser()] 
        return [IsOrderParticipant()]


    def get_queryset(self):
        """
        Returns all orders where the user is involved as customer or business.
        """
        user = self.request.user
        return Order.objects.filter(models.Q(customer_user=user) | models.Q(business_user=user))
    

    def get_serializer_class(self):
        """
        Uses OrderCreateSerializer for POST, OrderSerializer for GET.
        """
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer
    

    def perform_create(self, serializer):
        """
        Creates an Order from a given offer_detail_id.
        """
        offer_detail_id = serializer.validated_data['offer_detail_id']
        offer_detail = get_object_or_404(OfferDetail, pk=offer_detail_id)

        order = Order.objects.create(customer_user=self.request.user, business_user=offer_detail.offer.user, title=offer_detail.title,
            revisions=offer_detail.revisions, delivery_time_in_days=offer_detail.delivery_time_in_days, price=offer_detail.price,
            features=offer_detail.features, offer_type=offer_detail.offer_type, status='in_progress')

        self.response_data = OrderSerializer(order).data


    def create(self, request, *args, **kwargs):
        """
        Custom create method to return the serialized order after creation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(self.response_data, status=status.HTTP_201_CREATED)



class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):

    """
    Handles retrieving, updating, and deleting a single Order object.

    GET:
        - Returns the full order details.
        - Only accessible if the user is either the customer or business user.

    PATCH:
        - Only the business user may update the order status.
        - Validates that the new status is allowed.

    DELETE:
        - Only admin users may delete orders.
    """
      
    permission_classes = [IsAuthenticated, IsOrderOwner]
    serializer_class = OrderSerializer


    def get_queryset(self):
        """
        Returns orders where the authenticated user is involved.
        """
        user = self.request.user

        return Order.objects.filter(models.Q(customer_user=user) | models.Q(business_user=user))
    

    def partial_update(self, request, *args, **kwargs):
        """
        Allows the business user to update the order status.
        """

        order = self.get_object()

        if order.business_user != request.user:
            return Response({'detail': 'Only the business user can update the order status.'}, status=status.HTTP_403_FORBIDDEN)
        
        new_status = request.data.get('status')
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']

        if new_status not in valid_statuses:
            return Response({'detail': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        order.save()

        serializer =self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def destroy(self, request, *args, **kwargs):
        """
        Only admin users may delete orders.
        """
        if not request.user.is_staff:
            return Response({'detail': 'Only admin users can delete orders'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    

    def get_object(self):
        """
            Retrieve the order by its primary key (ID) from the URL.
            If the order does not exist, Django automatically returns a 404 response.

            Permission check:
            Only the business user or the customer user associated with this order
            is allowed to access it. If the requesting user is neither of them,
            raise a 403 Forbidden error.
        """
        order = get_object_or_404(Order, pk=self.kwargs['pk'])

        if order.business_user != self.request.user and order.customer_user != self.request.user:
            raise PermissionDenied('You do not have permission to access this order.')

        return order
    


class OrderCountView(APIView):

    """
    Returns the number of active (in_progress) orders for a given business user.

    GET:
        - business_user_id (URL parameter)
        - Validates that the user exists and is of type 'business'
        - Returns the count of orders where:
            business_user = given user AND status = 'in_progress'
    """
        
    permission_classes = [IsAuthenticated]


    def get(self, request, business_user_id):

        try:
            business_user = Profile.objects.get(id=business_user_id, type='business')
        except:
            return Response({'detail': 'Business user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({'order_count': order_count}, status=status.HTTP_200_OK)



class CompletedOrderCountView(APIView):

    """
    Returns the number of completed orders for a given business user.

    GET:
        - business_user_id (URL parameter)
        - Validates that the user exists and is of type 'business'
        - Returns the count of orders where:
            business_user = given user AND status = 'completed'
    """
     
    permission_classes = [IsAuthenticated]


    def get(self, request, business_user_id):

        try:
            business_user = Profile.objects.get(id=business_user_id, type='business')
        except Profile.DoesNotExist:
            return Response({'detail': 'Business user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()

        return Response({'completed_order_count': completed_order_count}, status=status.HTTP_200_OK)



class ReviewListCreateView(generics.ListCreateAPIView):

    """
    Handles listing and creating reviews.

    GET:
        - Returns all reviews ordered by newest first.

    POST:
        - Only customer users may create reviews.
        - A customer may only review a business user once.
        - Automatically assigns the authenticated user as the reviewer.
    """
        
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsCustomerReviewerorReadOnly]
    pagination_class = None

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {'business_user_id': ['exact'], 'reviewer_id': ['exact']}
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except ValidationError as exc:
            errors = exc.detail

            if isinstance(errors, list) and len(errors) == 1:
                normalized = {'detail': errors[0]}
            elif isinstance(errors, dict):
                normalized = {}
                for field, value in errors.items():
                    if isinstance(value, list) and len(value) == 1:
                        normalized[field] = value[0]
                    else:
                        normalized[field] = value
            else:
                normalized = {'detail': str(errors)}
            return Response(normalized, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def perform_create(self, serializer):
        reviewer = self.request.user
        business_user = serializer.validated_data['business_user']

        if reviewer.type != 'customer':
            raise ValidationError('Only customer profiles are allowed to create reviews.')
        
        if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists():
            raise ValidationError('You have already submitted a review for this business user.')

        serializer.save(reviewer=reviewer)



class ReviewDetailViewSet(generics.RetrieveUpdateDestroyAPIView):

    """
    Handles retrieving, updating, and deleting a single Review object.

    GET:
        - Returns the full review details.

    PATCH / PUT:
        - Only the reviewer (owner) may update the review.

    DELETE:
        - Only the reviewer (owner) may delete the review.
    """
        
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewerOwner]
    pagination_class = None



class ReviewViewSet(viewsets.ModelViewSet):

    """
    ViewSet for listing, retrieving, creating, updating, and deleting reviews.

    - GET: List all reviews ordered by newest first.
    - POST: Only customer users may create reviews.
    - PUT/PATCH: Only the reviewer may update their review.
    - DELETE: Only the reviewer may delete their review.
    """

    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsCustomerReviewerorReadOnly]


    def perform_create(self, serializer):
        """
        Automatically assigns the authenticated user as the reviewer.
        """
        serializer.save(reviewer=self.request.user)



class BaseInfoView(APIView):

    """
    Returns aggregated platform statistics for the dashboard.

    GET:
        - Total number of reviews
        - Average rating across all reviews
        - Number of business profiles
        - Number of offers
    """
        
    permission_classes = [AllowAny]


    def get(self, request):
        review_count = Review.objects.count()
        average_rating = round(Review.objects.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0, 1)
        business_profile_count = Profile.objects.filter(type='business').count()
        offer_count = Offer.objects.count()

        data = {
            'review_count': review_count,
            'average_rating': average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count
        }

        return Response(data, status=status.HTTP_200_OK)


