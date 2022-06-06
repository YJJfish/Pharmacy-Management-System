from django.urls import path, include, re_path
from django.views.generic import RedirectView


from doctor_interface import views

urlpatterns = [
    # Invoked by Doctor Frontend, in order to manipulate the database
    path('querymedicine/', views.QueryMedicine),
    path('prescmedicine/', views.PrescMedicine),
    path('querycart/', views.QueryCart),
]
