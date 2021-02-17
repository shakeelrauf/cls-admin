from django.urls import path, include
from .view.sheets.sheet1 import Sheet1View, Sheet1SalesPersonSummaryView, Sheet1SummaryView, Sheet1SummaryYearlyView
urlpatterns = [
    path('<sheet>', Sheet1View.as_view(), name='sheet_no'),
    path('<sheet>/year/<year>/person/<person>', Sheet1SalesPersonSummaryView.as_view(), name='sheet_no'),
    path('<sheet>/summary', Sheet1SummaryView.as_view(), name='sheet_no'),
    path('<sheet>/yearly/<year>', Sheet1SummaryYearlyView.as_view(), name='yearly'),
]