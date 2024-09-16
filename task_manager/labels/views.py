from typing import Any

from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin

from .models import Label
from .forms import LabelForm

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from task_manager.mixin import NoAuthMixin, NoPermissionMixin


class UseInTask(UserPassesTestMixin):
    index_url = reverse_lazy('index_labels')
    error_message = _("The label cannot be deleted because it is in use.")

    def test_func(self) -> bool | None:

        if self.request.method == 'POST':
            label = self.get_object()
            tasks = label.labels.all()

            return not tasks
        return True


class IndexLabels(NoPermissionMixin, NoAuthMixin, ListView):
    model = Label
    template_name = 'labels/index_labels.html'
    context_object_name = 'labels'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['messages'] = messages.get_messages(self.request)
        return context


class CreateLabel(NoPermissionMixin, NoAuthMixin, SuccessMessageMixin,
                  CreateView):
    form_class = LabelForm
    template_name = 'labels/create_label.html'
    success_url = reverse_lazy('index_labels')
    success_message = _('Label successfully created')


class UpdateLabel(NoPermissionMixin, NoAuthMixin, SuccessMessageMixin,
                  UpdateView):
    model = Label
    form_class = LabelForm
    template_name = 'labels/update_label.html'
    success_url = reverse_lazy('index_labels')
    success_message = _('Label successfully changed')


class DeleteLabel(NoPermissionMixin, NoAuthMixin, UseInTask,
                  SuccessMessageMixin, DeleteView):
    model = Label
    template_name = 'labels/delete_label.html'
    success_url = reverse_lazy('index_labels')
    success_message = _('Label deleted successfully')
