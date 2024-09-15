from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class NoAuthMixin(LoginRequiredMixin):
    redirect_field_name = ""

    def dispatch(self, request, *args, **kwargs):
        self.permission_denied_message = _(
            'You are not authorized! Please come in.')
        self.permission_denied_url = reverse_lazy('login')
        return super().dispatch(request, *args, **kwargs)


class NoPermissionMixin:
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, self.error_message)
            return redirect(self.index_url)
        else:
            messages.error(self.request, _(
                'You are not authorized! Please come in.'))
        return redirect(self.permission_denied_url)
