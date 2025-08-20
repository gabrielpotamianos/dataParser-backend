from datetime import timedelta
import time
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from backend import settings
from core.models import Candidates
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import Candidates
import re
import os
import requests


def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request: Request):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if not user:
            return Response({"detail": "Invalid credentials"}, status=400)
        else:
            token = Token.objects.get(user=user)
            if token and timezone.now() - token.created <= timedelta(minutes=15):
                pass
            else:
                Token.objects.filter(user=user).delete()
                token = Token.objects.create(user=user)
        print(token.key)
        print(token.created + timedelta(minutes=15))
        return Response(
            {
                "token": token.key,
                "expires_at": (token.created + timedelta(minutes=15)),
            }
        )


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def save_profile(request: Request):
    if request.method == "POST":
        token_key = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return Response({"detail": "Invalid token"}, status=401)

        if timezone.now() - token.created <= timedelta(minutes=15):
            profile_data = request.data.get("profileData")
            avatar_src = profile_data.pop("avatarUrl", None)
            profile_data = {camel_to_snake(k): v for k, v in profile_data.items()}

            if not isinstance(profile_data, dict):
                return Response({"detail": "Invalid profile data"}, status=400)

            profile, created = Candidates.objects.update_or_create(
                profile_url=profile_data["url"],
                defaults={**profile_data, "user": token.user},
            )

            if avatar_src:
                try:
                    # 3) fetch and write the file
                    resp = requests.get(avatar_src, timeout=5)
                    resp.raise_for_status()

                    # derive extension
                    ext = os.path.splitext(avatar_src)[1] or ".jpg"
                    filename = f"{profile.id}{ext}"
                    dest_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, filename)

                    with open(dest_path, "wb") as f:
                        f.write(resp.content)
                except Exception:
                    return Response({"detail": "Could not save image"}, status=500)

            return Response({"detail": "Profile saved"}, status=200)
        else:
            return Response({"detail": "Token expired"}, status=401)


@csrf_exempt
@api_view(["GET"])
@permission_classes([AllowAny])
def get_candidates(request):
    token_key = request.headers.get("Authorization", "").replace("Bearer ", "")
    try:
        token = Token.objects.get(key=token_key)
    except Token.DoesNotExist:
        return Response({"detail": "Invalid token"}, status=401)
    if timezone.now() - token.created > timedelta(minutes=15):
        return Response({"detail": "Token expired"}, status=401)

    public_base = settings.MEDIA_URL.rstrip("/") + "/avatars/"

    candidates = Candidates.objects.all()
    data = [
        {
            "id": c.id,
            "profile_url": c.profile_url,
            "full_name": c.full_name,
            "head_line": c.head_line,
            "location": c.location,
            "about": c.about,
            "education": c.education,
            "experience": c.experience,
            "skills": c.skills,
            "notes": c.notes,
            "url": c.url,
            "avatarUrl": f"{public_base}{c.id}.jpg",
        }
        for c in candidates
    ]
    return Response(data)
