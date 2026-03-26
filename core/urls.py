from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/score/', views.score_resume, name='score_resume'),
    path('api/generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('api/generate-pdf-direct/', views.generate_pdf_direct, name='generate_pdf_direct'),
]
