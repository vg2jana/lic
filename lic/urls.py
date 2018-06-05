from django.urls import path

from . import views

app_name = "lic"
urlpatterns = [
    # Root page
    path('', views.IndexView.as_view(), name='index'),

    # Client details page
    path('<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),

    # Policy details page
    path('<int:pk>/', views.PolicyDetailView.as_view(), name='policy_detail')
]