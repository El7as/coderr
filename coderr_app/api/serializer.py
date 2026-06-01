from rest_framework import serializers


from coderr_app.models import Offer, OfferDetail, Order, Review



class OfferDetailLinkSerializer(serializers.ModelSerializer):

    """
    Lightweight serializer used in Offer list responses.

    Instead of returning full OfferDetail objects, this serializer returns
    only the ID and a URL pointing to the detail endpoint. This keeps the
    Offer list response small and efficient while still allowing clients
    to fetch full detail data when needed.
    """
        
    url = serializers.SerializerMethodField()


    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


    def get_url(self, obj):
        """
        Returns the API URL for the OfferDetail instance.
        """
        return f'/offerdetails/{obj.id}/'



class OfferDetailSerializer(serializers.ModelSerializer):

    """
    Full serializer for OfferDetail objects.

    This serializer is used when returning complete detail information
    for an offer package (Basic, Standard, Premium). It includes pricing,
    delivery time, revision count, features, and the offer type.
    """

    price = serializers.FloatField()
    

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'description', 'price', 'delivery_time_in_days', 'revisions', 'features', 'offer_type']



class OfferdetailsSerializer(serializers.ModelSerializer):

    """
    Serializer used for returning a compact representation of OfferDetail.

    This serializer is typically used when the client needs a simplified
    version of the offer detail, such as in order creation or summary views.
    It includes only the essential fields: title, revisions, delivery time,
    price, features, and offer type.
    """

    price = serializers.FloatField()
    

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']



class OfferDetailPatchSerializer(serializers.ModelSerializer):

    """
    Serializer used for partial updates (PATCH) on OfferDetail objects.

    This serializer exposes only the fields that are allowed to be updated
    individually, such as title, revisions, delivery time, price, features,
    and offer type. It is typically used in endpoints where the client
    updates only a subset of fields rather than the entire object.
    """

    price = serializers.FloatField()
    

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']


    def validate(self, attrs):
        if 'offer_type' not in attrs or not attrs.get('offer_type'):
            raise serializers.ValidationError({'offer_type': 'This field is required for PATCH requests'})
        return attrs



class OfferPatchSerializer(serializers.ModelSerializer):

    """
    Serializer used for partial updates (PATCH) on Offer objects.

    This serializer exposes only the fields that are allowed to be updated
    individually, such as title, image, description, and nested offer details.
    The nested details are read-only here because they are updated through
    their own dedicated endpoints.
    """
        
    details = OfferDetailPatchSerializer(many=True)
      

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']


    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', [])
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        for detail_data in details_data:
            offer_type = detail_data.get('offer_type')
            if not offer_type:
                continue

            detail = OfferDetail.objects.filter(offer=instance, offer_type=offer_type).first()
            if detail:
                for attr, value in detail_data.items():
                    if value is not None:
                        setattr(detail, attr, value)
                detail.save()
            else:
                OfferDetail.objects.create(offer=instance, **detail_data)
        return instance
           


class OfferDetailViewSerializer(serializers.ModelSerializer):

    """
    Serializer used for returning full offer details including nested
    OfferDetail link objects.

    This serializer is typically used in Offer detail endpoints where
    the client needs complete information about the offer, including:
    - basic offer fields (title, image, description)
    - timestamps
    - minimum price and delivery time
    - nested detail links for Basic/Standard/Premium packages
    """
        
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.FloatField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details',
                  'min_price', 'min_delivery_time']
       


class OfferDetailPostSerializer(serializers.ModelSerializer):
    
    """
    Serializer used for creating new OfferDetail objects.

    This serializer is typically used when a business user creates
    a new offer package (Basic, Standard, Premium). It includes only
    the fields that are required for creation: title, revisions,
    delivery time, price, features, and offer type.
    """

    price = serializers.FloatField()

       
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features','offer_type']


    
class OfferPostSerializer(serializers.ModelSerializer):

    """
    Serializer used for creating new Offer objects along with their nested
    OfferDetail entries (Basic, Standard, Premium).

    This serializer expects a list of detail objects and handles the creation
    of both the Offer and its related OfferDetail instances. The authenticated
    user is automatically assigned as the offer owner.
    """

    details = OfferDetailPostSerializer(many=True, required=True)


    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        

    def create(self, validated_data):
        """
        Creates an Offer and its associated OfferDetail objects.

        Steps:
        - Extract nested detail data.
        - Create the Offer with the authenticated user.
        - Create each OfferDetail and link it to the Offer.
        - Attach all created details to the Offer.
        """
        details_data = validated_data.pop('details', [])
        offer = Offer.objects.create(user=self.context['request'].user, **validated_data)

        created_details = []
        for detail in details_data:
            created_detail = OfferDetail.objects.create(offer=offer, **detail)
            created_details.append(created_detail)

        offer.details.set(created_details)
        return offer



class OfferSerializer(serializers.ModelSerializer):

    """
    Main serializer for Offer objects.

    This serializer is used for listing and retrieving offers. It includes:
    - Basic offer information (title, image, description)
    - Timestamps
    - Minimum price and delivery time
    - Nested detail links for Basic/Standard/Premium packages
    - User details (first name, last name, username)
    """
    
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    user_details = serializers.SerializerMethodField(read_only=True)
    min_price = serializers.FloatField(read_only=True)
    

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details',
                  'min_price', 'min_delivery_time', 'user_details']
        
        extra_kwargs = {'user': {'required': False}}


    def get_user_details(self, obj):
        """
        Returns basic user information for the offer owner.
        """
        return {'first_name': obj.user.first_name, 'last_name': obj.user.last_name, 'username': obj.user.username}
    

    def validate(self, data):
        """
        Ensures the request body is not empty.
        """
        if not data:
            raise serializers.ValidationError("The body must not be empty.")
        return data
 


class OrderSerializer(serializers.ModelSerializer):

    """
    Serializer for returning full Order objects.

    This serializer is used for listing and retrieving orders. It includes:
    - Customer and business user references
    - Order metadata (title, revisions, delivery time, price, features)
    - Offer type and status
    - Creation and update timestamps
    """
    
    price = serializers.FloatField(read_only=True)


    class Meta:
        model = Order
        fields = ['id','customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                   'price','features', 'offer_type', 'status', 'created_at', 'updated_at']



class OrderCreateSerializer(serializers.Serializer):

    """
    Serializer used for creating an Order from a selected OfferDetail.

    The client provides only the `offer_detail_id`. The view using this
    serializer is responsible for:
    - validating that the OfferDetail exists
    - checking permissions (customer user, etc.)
    - creating the actual Order instance

    This serializer simply validates the input and returns the cleaned data.
    """
        
    offer_detail_id = serializers.IntegerField(write_only=True)


    def create(self, validated_data):
        """
        Returns the validated data. The actual Order creation is handled in the view, not here.
        """
        return validated_data
    
    def validate_offer_detail_id(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("A valid integer is required.")
        return value



class ReviewSerializer(serializers.ModelSerializer):

    """
    Serializer for returning full Review objects.

    This serializer is used for listing, retrieving, and creating reviews.
    It includes:
    - Business user being reviewed
    - Reviewer (customer)
    - Rating and description
    - Creation and update timestamps

    The reviewer and timestamps are read-only and automatically assigned.
    """
        
    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']
    

