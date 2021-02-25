from django.urls import path, include
from .views.dashboard import DashboardIndexView, SheetStatusView, RunSheetScriptView, update_sheet
from django.urls import path, include
from .views.sheets import get_json_sheet,get_winner, IndexView, SummaryView

urlpatterns = [
    path('dashboard/', DashboardIndexView.as_view()),
    path('update_sheet', update_sheet),
    path('dashboard/check_script_status', SheetStatusView.as_view()),
    path('dashboard/run_sheet_script/<sheet>', RunSheetScriptView.as_view()),
    path('', DashboardIndexView.as_view()),
    path('sheets/<sheet>', IndexView.as_view(), name='sheet_details'),
    path('sheets/<sheet>/summary', SummaryView.as_view(), name='sheet_summary'),
    path('sheets/<sheet>/summary/get_winner', get_winner, name='sheet_winner'),
    path('sheets/<sheet>/json', get_json_sheet, name='sheet_json'),
]