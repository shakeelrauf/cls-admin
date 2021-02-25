from django.urls import path, include
from .views.sheets import IndexView, data_table_server_side
urlpatterns = [
    path('sheets/<sheet>',IndexView.as_view()),
    path('sheets/<sheet>/datatable',data_table_server_side,name="server_side_table"),
]