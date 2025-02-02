from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class AdminRequiredMixin(UserPassesTestMixin):
    # Permissão de acesso apenas a usuários do grupo 'ADMINISTRADOR'

    def test_func(self):
        return self.request.user.groups.filter(name='ADMINISTRADOR').exists()

    def handle_no_permission(self):
        return redirect('semAcesso')