from django.shortcuts import render
from django.contrib.auth import authenticate

from requests import Request, Response
from rest_framework.authtoken.models import Token
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request: Request):
    print(request)
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        print(user)

        if not user:
            return Response({"detail": "Invalid credentials"}, status=400)
        else:
            token, _ = Token.objects.get_or_create(user=user)
            print(token)
            return Response({"token": token.key})
