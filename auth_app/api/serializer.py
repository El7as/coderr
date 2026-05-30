from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


from auth_app.models import Profile



class RegistrationSerializer(serializers.ModelSerializer):

    """
    Serializer for handling user registration.

    This serializer validates the incoming registration data, ensures that
    the password and repeated password match, and creates a new user using
    the custom Profile model. The serializer does not return the token
    directly; token creation is handled in the view.

    Fields:
        username (str): The desired username for the new account.
        email (str): The user's email address.
        password (str): The account password (write-only).
        repeated_password (str): Must match the password field.
        type (str): The user type ('customer' or 'business').
    """
       
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.CharField(write_only=True)


    class Meta:
        model = Profile
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}


    def validate(self, data):
        """
        Validate registration input.

        Ensures that the password and repeated_password fields match.
        Raises a ValidationError if they do not.

        Args:
            data (dict): The incoming registration data.

        Returns:
            dict: The validated data.

        Raises:
            ValidationError: If passwords do not match.
        """
                
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    

    def create(self, validated_data):
                
        """
        Create a new user account.

        Removes the repeated_password field, extracts the user type,
        and creates a new Profile instance using the custom user model.
        A token is also created for the new user.

        Args:
            validated_data (dict): The validated registration data.

        Returns:
            Profile: The newly created user instance.
        """
                
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type', None)
        user = Profile.objects.create_user(**validated_data, type=user_type)
        
        Token.objects.get_or_create(user=user)
        return user
    


class LoginSerializer(serializers.Serializer):
        
    """
    Serializer for handling user login authentication.

    This serializer validates the provided username and password using
    Django's `authenticate` function. If the credentials are valid, it
    returns an authentication token along with basic user information.
    If authentication fails, a validation error is raised.

    Fields:
        username (str): The username of the user attempting to log in.
        password (str): The user's password (write-only).
    """
        
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


    def validate(self, data):

        """
        Validate the provided login credentials.

        Args:
            data (dict): Contains 'username' and 'password'.

        Returns:
            dict: A dictionary containing the user's token, username,
                  email, and user ID if authentication succeeds.

        Raises:
            ValidationError: If the credentials are invalid.
        """
                
        user = authenticate(username=data['username'], password=data['password'])

        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        token, _ = Token.objects.get_or_create(user=user)
        return {'token': token.key, 'username': user.username, 'email': user.email, 'user_id': user.id}



class ProfileSerializer(serializers.ModelSerializer):

    """
    Serializer for representing full user profile data.

    This serializer is used when retrieving or updating a user's own profile.
    It exposes all relevant fields, including contact information, profile
    details, and metadata such as the creation timestamp. Optional fields are
    normalized to empty strings to ensure consistent API responses.

    Fields:
        user (int): The profile ID, exposed as 'user' for frontend compatibility.
    """
        
    user = serializers.IntegerField(source='id', read_only=True)


    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 
                  'description', 'working_hours', 'type', 'email', 'created_at']
        

    def to_representation(self, instance):

        """
        Customize the serialized output.

        Ensures that optional fields such as first_name, last_name, location,
        tel, description, and working_hours are returned as empty strings
        instead of null values. This prevents frontend handling issues and
        guarantees consistent API formatting.

        Args:
            instance (Profile): The profile instance being serialized.

        Returns:
            dict: The serialized and normalized profile data.
        """
                
        data = super().to_representation(instance)

        for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            if data.get(field) is None:
                data[field] = ''

        return data



class ProfileBusinessSerializer(serializers.ModelSerializer):

    """
    Serializer for representing business user profiles.

    This serializer exposes all relevant business-related fields such as
    location, telephone number, description, and working hours. It is used
    when listing or retrieving business profiles. Optional fields are
    normalized to empty strings to ensure consistent API responses.
    
    Fields:
        user (int): The profile ID, exposed as 'user' for frontend compatibility.
    """
        
    user = serializers.IntegerField(source='id', read_only=True)
   

    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 
                  'description', 'working_hours', 'type']
        
        def to_representation(self, instance):
            """
        Customize the serialized output.

        Ensures that optional fields such as first_name, last_name, location,
        tel, description, and working_hours are returned as empty strings
        instead of null values. This prevents frontend handling issues and
        guarantees consistent API formatting.

        Args:
            instance (Profile): The profile instance being serialized.

        Returns:
            dict: The serialized and normalized profile data.
            """
                    
            data = super().to_representation(instance)

            for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
                if data.get(field) is None:
                    data[field] = ''
            return data



class ProfileCustomerSerializer(serializers.ModelSerializer):

    """
    Serializer for representing customer profiles.

    This serializer exposes a limited set of fields intended for public
    display when listing or retrieving customer profiles. It includes
    basic identity information and the profile image. The serializer
    also normalizes empty fields to ensure consistent output.

    Fields:
        user (int): The profile ID, exposed as 'user' for frontend compatibility.
        updated_at (datetime): Mirrors 'created_at' for display purposes.
    """
        
    user = serializers.IntegerField(source='id', read_only=True)
    updated_at = serializers.DateTimeField(source='created_at', read_only=True)
   

    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'updated_at', 'type']
        
        def to_representation(self, instance):

            """
        Customize the serialized output.

        Ensures that optional fields such as first_name, last_name, and file
        are returned as empty strings instead of null values. This prevents
        frontend handling issues and ensures consistent API responses.

        Args:
            instance (Profile): The profile instance being serialized.

        Returns:
            dict: The serialized and normalized profile data.
            """
                    
            data = super().to_representation(instance)

            for field in ['first_name', 'last_name', 'file']:
                if data.get(field) is None:
                    data[field] = ''
            return data 



