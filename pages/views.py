"""Server-rendered page views."""
from django.shortcuts import render, redirect
from pages.auth import get_session_user


def index_view(request):
    """Homepage: redirect authenticated users to dashboard, others to login."""
    user = get_session_user(request)
    if user:
        return redirect('dashboard')
    return redirect('login')
