from django.urls import path
from .views import CustomLoginView, SemAcessoView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('sem-acesso/', SemAcessoView.as_view(), name='semAcesso')
]
