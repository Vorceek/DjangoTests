from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class AdminRequiredMixin(UserPassesTestMixin):

    # Permissão de acesso apenas a usuários do grupo 'ADMINISTRADOR'

    def test_func(self):
        return self.request.user.groups.filter(name='ADMINISTRADOR').exists()

    def handle_no_permission(self):
        return redirect('semAcesso')
    
def redirect_based_on_group(user):
        
    # Método auxiliar que realiza o redirecionamento com base no grupo do usuário.

    if user.groups.filter(name='ADMINISTRADOR').exists():
        return redirect('admin_app:hub')
    elif user.groups.filter(name='USER').exists():
        return redirect('user_app:home')
    else:
        return redirect('semAcesso')
    
def aside_icons(request):
    # Defina os ícones desejados:
    icons = [
        {'link': '/user-base/', 'icon_name': 'plus-circle', 'is_admin': True},
        {'link': '/admin-base/relatorio/', 'icon_name': 'file-text', 'is_admin': True},
        #{'link': '/admin-base/relatorio/', 'icon_name': 'file-text', 'is_admin': True},

    ]
    
    is_admin = request.user.is_authenticated and request.user.groups.filter(name='ADMINISTRADOR').exists()
    is_user = request.user.is_authenticated and request.user.groups.filter(name='USER').exists()
    
    return {
        'aside_icons': icons,
        'is_admin': is_admin,
        'is_user': is_user,
    }