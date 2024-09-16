from typing import Any
from django.http import HttpRequest, HttpResponse
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect

from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import Status
from .forms import StatusForm

from task_manager.mixin import NoAuthMixin, NoPermissionMixin


class IndexStatuses(NoPermissionMixin, NoAuthMixin, ListView):
    model = Status
    template_name = 'statuses/index_statuses.html'
    context_object_name = 'statuses'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['messages'] = messages.get_messages(self.request)
        return context


class CreateStatus(NoPermissionMixin, NoAuthMixin, SuccessMessageMixin,
                   CreateView):
    form_class = StatusForm
    template_name = 'statuses/create_status.html'
    success_url = reverse_lazy('index_statuses')
    success_message = _('Status successfully created')


class UpdateStatus(NoPermissionMixin, NoAuthMixin, SuccessMessageMixin,
                   UpdateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/update_status.html'
    success_url = reverse_lazy('index_statuses')
    success_message = _('Status successfully changed')


class DeleteStatus(NoPermissionMixin, NoAuthMixin, SuccessMessageMixin,
                   DeleteView):
    model = Status
    template_name = 'statuses/delete_status.html'
    success_url = reverse_lazy('index_statuses')
    success_message = _('Status deleted successfully')
    error_del_message = _("The status cannot be deleted because it is in use.")

    def post(self,
             request: HttpRequest,
             *args: str,
             **kwargs: Any) -> HttpResponse:
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.add_message(request, messages.ERROR,
                                 self.error_del_message)
            return redirect(reverse_lazy('index_statuses'))
