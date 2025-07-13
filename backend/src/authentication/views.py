from django.shortcuts import render

# Create your views here.
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.db.models import Q

from ai_review.celery_worker import send_otp_email

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from account.models import User
from account.serailizers import AccountSerializer
from .utils import WrongCredential
from .error import CustomError, CustomErrorAsDict

import json

import redis

redis_client = redis.StrictRedis(host="redis", port=6379, db=0)

import logging

logger = logging.getLogger(__name__)


class RequestOTPView(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            key = request.data.get("key")

            # Validation
            valid_keys = ["sign_up_otp", "reset_password_otp", "log_in_otp"]
            if key not in valid_keys:
                raise CustomErrorAsDict({"error": "Invalid OTP key"})

            if key == "sign_up_otp":
                username = request.data.get("username")
                password = request.data.get("password")
                confirm_password = request.data.get("confirm_password")
                confirm_email = request.data.get("confirm_email")

                if User.objects.filter(username=username).exists():
                    raise CustomErrorAsDict({"error": "Username is already taken"})
                if User.objects.filter(email=email).exists():
                    raise CustomErrorAsDict({"error": "Email is already taken"})
                if email != confirm_email:
                    raise CustomErrorAsDict({"error": "Email does not match"})
                if password != confirm_password:
                    raise CustomErrorAsDict({"error": "Password does not match"})

            else:
                get_object_or_404(User, email=email)

            # Delete any existing OTP for the user and key
            redis_client.delete(f"{key}:{email}")

            send_otp_email(email, key)
            return Response(
                {"message": "OTP sent to your email"}, status=status.HTTP_200_OK
            )

        except Http404:
            logger.error(f"User not found")
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except CustomErrorAsDict as error:
            logger.error(f"Invalid requesting OTP: {error.error}")
            return Response({"error": error.error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            logger.error(f"Error while requesting OTP: {str(error)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ValidateOTPView(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            key = request.data.get("key")
            otp = request.data.get("otp")

            # Validation
            valid_keys = ["sign_up_otp", "reset_password_otp", "log_in_otp"]
            if key not in valid_keys:
                raise CustomErrorAsDict({"error": "Invalid OTP key"})

            otp_data = redis_client.get(f"{key}:{email}").decode("utf-8")
            if not otp_data:
                raise CustomErrorAsDict({"error": "Invalid OTP or OTP has expired"})
            if otp_data != otp:
                raise CustomErrorAsDict({"error": "Invalid OTP"})

            if key == "sign_up_otp":
                username = request.data.get("username")
                password = request.data.get("password")
                User.objects.create_user(username, email, password)

                # Delete any existing OTP for the user and key
                redis_client.delete(f"{key}:{email}")
                return Response(
                    {"message": "User verify OTP for sign up successfully"},
                    status=status.HTTP_200_OK,
                )

            elif key == "reset_password_otp":
                return Response(
                    {"message": "User verify OTP for reset password successfully"},
                    status=status.HTTP_200_OK,
                )

            else:
                user = get_object_or_404(User, email=email)
                login(request, user)

                if not user:
                    raise WrongCredential("Wrong credential")

                # Create token for user
                token_obj = Token.objects.get_or_create(user=user)[0]

                # Delete any existing OTP for the user and key
                redis_client.delete(f"{key}:{email}")

                logger.info(f"{user.username} login success using identifier({email}).")
                return JsonResponse({"token": token_obj.key}, status=status.HTTP_200_OK)

        except Http404:
            logger.error("User not found")
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except CustomErrorAsDict as error:
            logger.error(f"Invalid validation OTP: {error.error}")
            return Response({"error": error.error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            logger.error(f"Error while validation OTP: {str(error)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetPassword(APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            confirm_password = request.data.get("confirm_password")
            otp = request.data.get("otp")
            key = request.data.get("key")

            # Validation
            if key != "reset_password_otp":
                raise CustomErrorAsDict({"error": "Invalid OTP key"})

            if password != confirm_password:
                raise CustomErrorAsDict({"error": "Password does not match"})

            otp_data = redis_client.get(f"{key}:{email}").decode("utf-8")
            if not otp_data:
                raise CustomErrorAsDict({"error": "Invalid OTP or OTP has expired"})
            if otp_data != otp:
                raise CustomErrorAsDict({"error": "Invalid OTP"})

            user = get_object_or_404(User, email=email)
            user.set_password(password)
            user.save()

            # Delete any existing OTP for the user and key
            redis_client.delete(f"{key}:{email}")

            return Response(
                {"message": "Reset password successfully"}, status=status.HTTP_200_OK
            )

        except Http404:
            logger.error("User not found")
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except CustomErrorAsDict as error:
            logger.error(f"Invalid reset password: {error.error}")
            return Response({"error": error.error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            logger.error(f"Error while reset password: {str(error)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Login user
            @param identifier: string (username or email)
            @param password: string
        """
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        # Validate input
        if not identifier or not password:
            logger.info(f"Login failed: Missing identifier or password")
            return Response(
                {"error": "Both identifier and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Try to find user by username or email
            try:
                user = User.objects.filter(
                    Q(username=identifier) | Q(email=identifier)
                ).first()
                if not user:
                    raise WrongCredential("Invalid username or email")
            except User.DoesNotExist:
                raise WrongCredential("Invalid username or email")

            # Check if user is active
            if not user.is_active:
                logger.info(f"Login failed for {identifier}: User is inactive")
                return Response(
                    {"error": "User account is not active"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Authenticate user
            user = authenticate(request, username=user.username, password=password)
            if not user:
                logger.info(f"Login failed for {identifier}: Incorrect password")
                return Response(
                    {"error": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED
                )

            # Login user
            login(request, user)

            # Create or retrieve token
            token, _ = Token.objects.get_or_create(user=user)

            logger.info(
                f"Login successful for {user.username} using identifier {identifier}"
            )
            return Response({"token": token.key}, status=status.HTTP_200_OK)

        except WrongCredential as error:
            logger.info(f"Login failed for {identifier}: {str(error)}")
            return Response({"error": str(error)}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as error:
            logger.exception(
                f"Unexpected error during login for {identifier}: {str(error)}"
            )
            return Response(
                {"error": "Internal server error"},
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
            logger.info(f"{username} logged out.")
            return Response(status=status.HTTP_200_OK)

        except Exception as error:
            logger.exception(f"Error while logger out: {str(error)}")
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
            logger.exception(f"Error while getting current user: {str(error)}")
            return JsonResponse(
                {
                    "error": "Internal server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
