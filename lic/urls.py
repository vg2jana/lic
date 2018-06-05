from django.urls import path

from . import views

app_name = "lic"
urlpatterns = [
    # Root page
    path('', views.index, name='index'),

    # Clients page
    path('clients', views.Clients.as_view(), name='clients'),

    # Root page
    path('reminders', views.index, name='reminders'),

    # Root page
    path('status', views.index, name='status'),

    # Client details page
    path('<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),

    # Policy details page
    path('<int:pk>/', views.PolicyDetailView.as_view(), name='policy_detail')
]