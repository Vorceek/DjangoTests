from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.base_app.permissions import AdminRequiredMixin

class AdminView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "admin/hub.html"
