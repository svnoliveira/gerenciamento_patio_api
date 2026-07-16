from django.urls import path
from .views import ExcelImportView, ExternalApiSyncView

urlpatterns = [
    path("integrations/excel-import/", ExcelImportView.as_view()),
    path("integrations/external-sync/", ExternalApiSyncView.as_view()),
]
