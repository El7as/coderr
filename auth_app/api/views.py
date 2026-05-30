from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from django.core.exceptions import PermissionDenied


from auth_app.models import Profile
from .serializer import RegistrationSerializer, LoginSerializer, ProfileSerializer, ProfileBusinessSerializer, ProfileCustomerSerializer



class RegistrationView(APIView):

    """
    API endpoint for user registration.

    This view handles the creation of new user accounts. Incoming data is
    validated using the RegistrationSerializer. If the data is valid, a new
    user is created and an authentication token is generated for immediate
    login. The response includes the token and basic user information.

    Methods:
        post(request):
            Validates registration data, creates a new user, and returns
            authentication details or validation errors.
    """

    permission_classes = [AllowAny]

    def post(self, request):

        """
        Handle POST requests for user registration.

        Args:
            request (Request): The incoming HTTP request containing
            registration fields such as username, email, password, and type.

        Returns:
            Response:
                - 201 Created with token and user data if registration succeeds.
                - 400 Bad Request with validation errors if input is invalid.
        """
                
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response({'token':token.key, 'username': user.username, 'email': user.email, 'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LoginView(APIView):

    """
    API endpoint for user authentication.

    This view handles user login by validating the provided credentials
    using the LoginSerializer. If the credentials are valid, the serializer
    returns the user's authentication token along with basic profile data.
    If validation fails, a 400 Bad Request response is returned.

    Methods:
        post(request):
            Validates the incoming login data and returns either the
            authenticated user data or validation errors.
    """

    permission_classes = [AllowAny]


    def post(self, request):

        """
        Handle POST requests for user login.

        Args:
            request (Request): The incoming HTTP request containing
            'username' and 'password' fields.

        Returns:
            Response:
                - 200 OK with token and user data if credentials are valid.
                - 400 Bad Request with error details if validation fails.
        """
                
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class ProfileDetailView(generics.RetrieveUpdateAPIView):

    """
    API endpoint for retrieving and updating a single user profile.

    This view allows authenticated users to:
    - Retrieve any profile (GET)
    - Update only their own profile (PUT/PATCH)

    The `get_object()` method enforces that users may only modify
    their own profile. Attempting to update another user's profile
    results in a PermissionDenied exception.

    Attributes:
        queryset (QuerySet): All Profile objects.
        serializer_class (Serializer): Serializer used for profile output.
        permission_classes (list): Requires the user to be authenticated.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


    def get_object(self):

        """
        Retrieve the profile instance and enforce ownership rules.

        Returns:
            Profile: The profile instance requested.

        Raises:
            PermissionDenied: If the authenticated user attempts to
            update a profile that does not belong to them.
        """
           
        profile = super().get_object()

        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            if profile.id != self.request.user.id:
                raise PermissionDenied('You may only edit your own profile.')
            return profile
   


class BusinessProfilListView(generics.ListAPIView):

    """
    API endpoint that returns a list of all business profiles.

    This view filters the Profile model to include only users with
    type='business'. It is accessible only to authenticated users.
    Pagination is disabled so the full list is returned in a single response.

    Attributes:
        queryset (QuerySet): All Profile objects where type='business'.
        serializer_class (Serializer): Serializer used to format the output.
        permission_classes (list): Requires the user to be authenticated.
        pagination_class (None): Disables pagination for this endpoint.
    """

    queryset = Profile.objects.filter(type='business')
    serializer_class = ProfileBusinessSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None



class CustomerProfilListView(generics.ListAPIView):

    """
    API endpoint that returns a list of all customer profiles.

    This view filters the Profile model to include only users with
    type='customer'. It is accessible only to authenticated users.
    Pagination is disabled to return the full list in a single response.

    Attributes:
        queryset (QuerySet): All Profile objects where type='customer'.
        serializer_class (Serializer): Serializer used to format output.
        permission_classes (list): Requires the user to be authenticated.
        pagination_class (None): Disables pagination for this endpoint.
    """

    queryset = Profile.objects.filter(type='customer')
    serializer_class = ProfileCustomerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


