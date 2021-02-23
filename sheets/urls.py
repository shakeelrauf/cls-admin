from django.urls import path, include
from .view.sheets.sheets import get_json_sheet,get_winner, IndexView, SummaryView
urlpatterns = [
    path('<sheet>', IndexView.as_view(), name='sheet_details'),
    path('<sheet>/summary', SummaryView.as_view(), name='sheet_summary'),
    path('<sheet>/summary/get_winner', get_winner, name='sheet_winner'),
    path('<sheet>/json', get_json_sheet, name='sheet_json'),
]