from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexIndex.as_view(), name='index_users'),
    path('create/', views.CreateUser.as_view(), name='create_user'),
    path('<int:id>/update/', views.UpdateUser.as_view(), name='update_user'),
    path('<int:id>/delete/', views.DeleteUser.as_view(), name='delete_user'),
]
