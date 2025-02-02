from django.views import View
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic.base import TemplateView

class SemAcessoView(TemplateView):
    template_name = 'login/semAcesso.html'

class CustomLoginView(View):

    def get(self, request):

        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'login/login.html')
    
    def post(self, request):

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.groups.filter(name ='ADMINISTRADOR').exists(): return redirect('hub')
            elif user.groups.filter(name = 'USER').exists(): return redirect('home')
            else: return redirect('semAcesso')

        else:
            messages.error(request, 'Credenciais inválidas. Tente novamente.')
            return render(request, 'login/login.html')

class LogoutAction(View):

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)  # Encerra a sessão do usuário
        return redirect('login')  # Redireciona para a página de login