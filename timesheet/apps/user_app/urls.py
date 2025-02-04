from django.urls import path
from .views import GerenciarAtividadesView

app_name = 'user_app'

urlpatterns = [
    path('', GerenciarAtividadesView.as_view(), name='home'),
]
