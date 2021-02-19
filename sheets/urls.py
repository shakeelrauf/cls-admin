from django.urls import path, include
from .view.sheets.sheet1 import run_script,get_json_sheet,get_winner, Sheet1View, Sheet1SalesPersonSummaryView, Sheet1SummaryView, Sheet1SummaryYearlyView
urlpatterns = [
    path('<sheet>/year/<year>/person/<person>', Sheet1SalesPersonSummaryView.as_view(), name='sheet_no'),
    path('<sheet>/summary', Sheet1SummaryView.as_view(), name='sheet_no'),
    path('<sheet>/summary/get_winner', get_winner, name='sheet_no'),
    path('<sheet>/yearly/<year>', Sheet1SummaryYearlyView.as_view(), name='yearly'),
    path('<sheet>/json', get_json_sheet),
    path('run_script', run_script)
]