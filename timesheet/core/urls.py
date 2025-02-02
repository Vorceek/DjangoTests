from django.contrib import admin
from django.urls import path, include
from apps.base_app.views import CustomLoginView, SemAcessoView, LogoutAction

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutAction.as_view(), name='logout'),
    path('sem-acesso/', SemAcessoView.as_view(), name='semAcesso'),

    path('user-base/', include('apps.user_app.urls')),
    path('admin-base/', include('apps.admin_app.urls')),
]