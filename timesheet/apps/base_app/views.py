from django.views import View
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic.base import TemplateView
from .permissions import redirect_based_on_group

class SemAcessoView(TemplateView):
    template_name = 'login/semAcesso.html'

class CustomLoginView(View):

    def get(self, request):

        if request.user.is_authenticated:
            return redirect_based_on_group(request.user)
        
        return render(request, 'login/login.html')
    
    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me', False)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if remember_me:

                request.session.set_expiry(1209600)  # 2 semanas de sessão
                response = redirect('home')  # Redireciona para a página inicial
                response.set_cookie('username', username, max_age=1209600)
                return response
            
            else: return redirect_based_on_group(self, user)

        else:
            messages.error(request, 'Credenciais inválidas. Tente novamente.')
            return render(request, 'login/login.html')

class LogoutAction(View):

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)  # Encerra a sessão do usuário
        return redirect('login')  # Redireciona para a página de login