from django.urls import path

from . import views

app_name = "lic"
urlpatterns = [
    # Root page
    path('', views.index, name='index'),

    # Clients page
    path('clients', views.all_clients, name='all_clients'),

    # Root page
    path('dues', views.dues, name='dues'),

    # Root page
    path('reminders', views.index, name='reminders'),

    # Root page
    path('status', views.index, name='status'),

    # Due submit
    path('due_submit/<int:pk>', views.due_submit, name='due_submit'),

    # Client details page
    path('<int:client_id>/', views.client_detail, name='client_detail'),

    # Policy details page
    path('<int:pk>/', views.PolicyDetailView.as_view(), name='policy_detail'),

    # Due json
    path('due_json/<int:pk>/', views.due_json, name='due_json')
]