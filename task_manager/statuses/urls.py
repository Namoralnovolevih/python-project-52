from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexStatuses.as_view(), name='index_statuses'),
    path('create/', views.CreateStatus.as_view(), name='create_status'),
    path('<int:pk>/update/',
         views.UpdateStatus.as_view(),
         name='update_status'),
    path('<int:pk>/delete/',
         views.DeleteStatus.as_view(),
         name='delete_status'),
]
