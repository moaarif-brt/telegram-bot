from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *

class LoginView(FormView):
    template_name = "auth/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        identifier = form.cleaned_data["identifier"]
        password = form.cleaned_data["password"]

        # Try to authenticate using username
        user = authenticate(self.request, username=identifier, password=password)

        # If authentication fails, check if it's an email and get the username
        if user is None:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(self.request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        # Authenticate and login the user
        if user is not None:
            login(self.request, user)
            return HttpResponseRedirect(reverse("dashboard"))  # Redirect after login
        else:
            form.add_error(None, "Invalid username/email or password")
            return self.form_invalid(form)

from django.core.paginator import Paginator

class TokenDashboardView(LoginRequiredMixin, View):
    template_name = "bot/dashboard.html"
    def handle_no_permission(self):
        login_url = reverse('login')  # Get the URL for the login view
        return HttpResponseForbidden(f"<H2>You are not authorized to access this page. Please <a href='{login_url}'>Login</a>!</H2>")
    def get(self, request):
        query = request.GET.get("q", "").strip()  # Get the search query from the URL
        tokens = Token.objects.filter(user=request.user)  # Fetch only the logged-in user's tokens

        if query:
            tokens = tokens.filter(
                token_symbol__icontains=query
            ) | tokens.filter(
                token_name__icontains=query
            )  # Filter by symbol or name (case-insensitive)
        # Pagination
        paginator = Paginator(tokens,10)  # Show 20 tokens per page
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        form = TokenForm()
        return render(request, self.template_name, {
                    "tokens": page_obj,  # Pass paginated tokens
                    "query": query,
                    "form": form,
                    "paginator": paginator,
                    "page_obj": page_obj,
                })    
    def post(self, request):
        form = TokenForm(request.POST)
        if form.is_valid():
            token = form.save(commit=False)
            token.user = request.user  # Assign the logged-in user
            token.save()
            
            # Add a success message
            messages.success(request, "Token added successfully!")
            return redirect('dashboard')  # Redirect after successful entry
        
        # In case of form errors, add an error message
        messages.error(request, "There was an error adding the token. Please check the form.")
        
        # Reload the page with the form errors
        return self.get(request)

class TokenDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            token = Token.objects.get(pk=pk, user=request.user)
            token.delete()
            messages.success(request, "Token deleted successfully.")
        except Token.DoesNotExist:
            messages.error(request, "Token not found.")
        return redirect('dashboard')
    

class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('login')