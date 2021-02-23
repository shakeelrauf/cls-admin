from django.urls import path, include
from .views import DashboardIndexView, SheetStatusView, RunSheetScriptView, update_sheet

urlpatterns = [
    path('dashboard/', DashboardIndexView.as_view()),
    path('update_sheet', update_sheet),
    path('dashboard/check_script_status', SheetStatusView.as_view()),
    path('dashboard/run_sheet_script/<sheet>', RunSheetScriptView.as_view()),
    path('', DashboardIndexView.as_view())
]