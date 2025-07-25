# vase_table_sim/urls.py
from django.urls import path
from .views import simulate_table_vase

urlpatterns = [
    path('simulate/',simulate_table_vase),
]