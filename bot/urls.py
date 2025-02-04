
from django.urls import path
from .views import *

urlpatterns = [
    path("", LoginView.as_view(), name="login"),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path("dashboard/", TokenDashboardView.as_view(), name="dashboard"),
    path('delete-token/<int:pk>/', TokenDeleteView.as_view(), name='delete_token'),
]
