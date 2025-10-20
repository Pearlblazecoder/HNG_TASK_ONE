from django.urls import path
from .views import (
    StringAnalysisListCreateView, 
    NaturalLanguageFilterView,
    StringAnalysisBulkView,
    HealthCheckView,
    StringAnalysisRetrieveDeleteView,
    URLDebugView
)

urlpatterns = [
    path('debug-urls', URLDebugView.as_view(), name='debug-urls'),
    path('strings', StringAnalysisListCreateView.as_view(), name='string-list-create'),
    path('strings/filter-by-natural-language', NaturalLanguageFilterView.as_view(), name='natural-language-filter'),    
    path('strings/<str:string_value>', StringAnalysisRetrieveDeleteView.as_view(), name='string-retrieve-delete'),
    path('strings/bulk', StringAnalysisBulkView.as_view(), name='string-bulk'),
    path('health', HealthCheckView.as_view(), name='health-check'),
]