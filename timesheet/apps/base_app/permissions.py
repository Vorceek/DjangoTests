from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from .models import Cliente, Servico, Atividade
from django.core.paginator import Paginator

class AdminRequiredMixin(UserPassesTestMixin):

    # Permissão de acesso apenas a usuários do grupo 'ADMINISTRADOR'

    def test_func(self):
        return self.request.user.groups.filter(name='ADMINISTRADOR').exists()

    def handle_no_permission(self):
        return redirect('semAcesso')


class BaseDataMixin:
    def get_base_context(self):
        user = self.request.user
        grupos = user.groups.all()
        return {
            'clientes': Cliente.objects.filter(setor__in=grupos).distinct().order_by('nome'),
            'servicos': Servico.objects.filter(setor__in=grupos).distinct().order_by('nome'),
            'atividades': Atividade.objects.filter(setor__in=grupos).distinct().order_by('nome'),
            'is_admin': user.groups.filter(name='Admin').exists(),
        }
    
    def get_context_data(self, **kwargs):
        context = self.get_base_context()
        context.update(kwargs)
        return context
    

class PaginationMixin:
    pagination_per_page = 20  # valor padrão, pode ser sobrescrito

    def get_paginated_context(self, queryset, context_key='page_obj'):
        """
        Recebe um queryset, pagina os resultados com base na requisição e retorna um dicionário
        contendo o objeto de paginação e o queryset completo.
        """
        paginator = Paginator(queryset, self.pagination_per_page)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return {context_key: page_obj, 'object_list': queryset}


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