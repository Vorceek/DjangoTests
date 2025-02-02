from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class UserView(LoginRequiredMixin, TemplateView):
    template_name = "user/home.html"
