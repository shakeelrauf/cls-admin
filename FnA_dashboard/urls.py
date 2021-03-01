from django.urls import path, include
from .views.sheets import IndexView, data_table_server_side, get_PO_LED
urlpatterns = [
    path('sheets/<sheet>',IndexView.as_view()),
    path('sheets/<sheet>/datatable',data_table_server_side,name="server_side_table"),
    path('po_leds/<po>',get_PO_LED,name="po_leds"),
]