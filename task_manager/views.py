from django.shortcuts import render
from django.views import View
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin

from .forms import LoginUserForm


class IndexView(View):
    def get(self, request, *args, **kwargs):
        messages_ = messages.get_messages(request)

        return render(
            request,
            'index.html',
            context={
                'messages': messages_
            }
        )


class LoginUser(SuccessMessageMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'login.html'
    success_message = _('You are logged in')


class LogoutUser(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, _("You are logged out."))
        return super().dispatch(request, *args, **kwargs)
