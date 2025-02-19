from django.shortcuts import render

# Create your views here.
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from account.models import User

from account.serailizers import AccountSerializer
from .utils import WrongCredential
from .error import CustomError, CustomErrorAsDict

import logging

logging = logging.getLogger(__name__)


class SignUp(APIView):

    def post(self, request):
        """
        Register new user
            @param username: string
            @param password: string
            @param confirm_password: string
            @param email: string
            @param confirm_email: string
        """
        username = request.data.get("username")
        password = request.data.get("password")
        confirm_password = request.data.get("confirm_password")
        email = request.data.get("email")
        confirm_email = request.data.get("confirm_email")

        try:

            # Check matching password
            if password != confirm_password:
                raise CustomErrorAsDict(
                    {
                        "error": "Password does not match",
                    }
                )

            # Check matching email
            if email != confirm_email:
                raise CustomErrorAsDict(
                    {
                        "error": "Email does not match",
                    }
                )

            # Check password
            if password != confirm_password:
                raise CustomErrorAsDict(
                    {
                        "error": "Password does not match",
                    }
                )

            # Check email
            if email != confirm_email:
                raise CustomErrorAsDict(
                    {
                        "error": "Email does not match",
                    }
                )

            # Check if username is already taken
            if User.objects.filter(username=username).exists():
                raise CustomErrorAsDict(
                    {
                        "error": "Username is already taken",
                    }
                )

            # Create user
            User.objects.create_user(username, email, password)

            logging.info(f"User {username} registered.")
            return JsonResponse({"message": "OK"}, status=status.HTTP_200_OK)

        except CustomErrorAsDict as error:
            logging.error(f"Invalid registration: {error.error}")
            return JsonResponse(
                {
                    "error": error.error,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as error:
            logging.error(f"Error while registering user: {str(error)}")
            return JsonResponse(
                {
                    "error": "Internal server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Login user
            @param identifier: string
            @param password: string
        """
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        try:
            # Check if identifier and password are provided
            if not identifier or not password:
                raise CustomError("Invalid authentication data")

            # Get the account_user object by the type of identifier
            if "@" in identifier:
                account_user_obj = get_object_or_404(User, email=identifier)
            else:
                account_user_obj = get_object_or_404(User, username=identifier)

            # Check if user is active
            if not account_user_obj.is_active:
                raise CustomErrorAsDict(
                    {
                        "error": "User is not active",
                    }
                )

            # Authenticate user
            user = authenticate(
                request, username=account_user_obj.get_username(), password=password
            )
            
            # Loging
            login(request, user)

            if not user:
                raise WrongCredential("Wrong credential")

            # Create token for user
            token_obj = Token.objects.get_or_create(user=user)[0]

            logging.info(f"{account_user_obj.username} login success using identifier({identifier}).")
            return JsonResponse({"token": token_obj.key}, status=status.HTTP_200_OK)

        except (CustomError, Http404, WrongCredential) as error:
            logging.info(f"identifier({identifier}) login failed: {str(error)}")

            if type(error) == Http404:
                response_status = status.HTTP_404_NOT_FOUND
                response_message = "Username, email, or password is incorrect"

            elif type(error) == WrongCredential:
                response_status = status.HTTP_404_NOT_FOUND
                response_message = "Username, email, or password is incorrect"

            else:
                response_status = status.HTTP_400_BAD_REQUEST
                response_message = str(error)

            return JsonResponse(
                {
                    "error": response_message,
                },
                status=response_status,
            )

        except CustomErrorAsDict as error:
            logging.info(f"identifier({identifier}) login failed: {str(error)}")
            return JsonResponse(
                {
                    "error": error.error,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as error:
            logging.exception(f"Error while identifier({identifier}) trying to login: {str(error)}")
            return JsonResponse(
                {
                    "error": "Internal server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Logout user
        """
        try:
            request.user.auth_token.delete()

            username = request.user.username
            logging.info(f"{username} logged out.")
            return Response(status=status.HTTP_200_OK)

        except Exception as error:
            logging.exception(f"Error while logging out: {str(error)}")
            return JsonResponse(
                {
                    "error": "Internal server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CurrentUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get current user
        """
        try:
            if not request.user.is_authenticated:
                return JsonResponse(
                    {
                        "error": "Unauthorized",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            return JsonResponse(AccountSerializer(request.user).data)

        except Exception as error:
            logging.exception(f"Error while getting current user: {str(error)}")
            return JsonResponse(
                {
                    "error": "Internal server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
