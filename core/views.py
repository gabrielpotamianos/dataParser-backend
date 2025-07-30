from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from core.models import Candidates
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Candidates
import re


def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request: Request):
    print(request)
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response({"detail": "Invalid credentials"}, status=400)
        else:
            Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            print(token)
            return Response({"token": token.key})


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def save_profile(request: Request):
    print("Saving Profile Request Done")
    if request.method == "POST":
        token_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        print(request.headers)
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=401)
        print("TOKEN CREATED AT: ")
        print(token.created)
        if timezone.now() - token.created <= timedelta(minutes=15):
            profile_data = request.data.get("profileData")
            profile_data = {camel_to_snake(k): v for k, v in profile_data.items()}
            if not isinstance(profile_data, dict):
                return Response({"detail": "Invalid profile data"}, status=400)
            profile, created = Candidates.objects.update_or_create(
                user=token.user, defaults=profile_data, created_at=timezone.now()
            )
            return Response({"detail": "Profile saved"}, status=200)
        else:
            return Response({"detail": "Token expired"}, status=401)
