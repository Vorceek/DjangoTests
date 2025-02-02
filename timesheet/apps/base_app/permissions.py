from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class AdminRequiredMixin(UserPassesTestMixin):

    # Permissão de acesso apenas a usuários do grupo 'ADMINISTRADOR'

    def test_func(self):
        return self.request.user.groups.filter(name='ADMINISTRADOR').exists()

    def handle_no_permission(self):
        return redirect('semAcesso')
    
def redirect_based_on_group(self, user):
        
    # Método auxiliar que realiza o redirecionamento com base no grupo do usuário.
        
    if user.groups.filter(name='ADMINISTRADOR').exists():
        return redirect('hub')
    elif user.groups.filter(name='USER').exists():
        return redirect('home')
    else:
        return redirect('semAcesso')