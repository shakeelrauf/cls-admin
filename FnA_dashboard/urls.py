from django.urls import path, include
from .views.sheets import update_follow_up_date, submit_pos, IndexView,update_r3_PO_LED, data_table_server_side, get_r3_PO_LED, get_r3d_PO_LED, update_department, select_primary_warehouse
from .views.dashboard import DepartmentDashboard, dashboard_datatable

app_name = "fna_urls"
urlpatterns = [
    path('sheets/<sheet>',IndexView.as_view()),
    path('sheets/<sheet>/datatable',data_table_server_side,name="server_side_table"),
    path('po_r3_leds/<po>',get_r3_PO_LED,name="po_r3_leds"),
    path('po_r3d_leds/<po>',get_r3d_PO_LED,name="po_r3d_leds"),
    path('update_r_3', update_r3_PO_LED, name="update_po_led"),
    path('submit_pos', submit_pos, name='submit_pos'),
    path('update_follow_up_date', update_follow_up_date, name='update_follow_up_date'),

    path('update_department', update_department, name='update_department'),
    path('dashboard/<department_name>', DepartmentDashboard.as_view(), name="department_dashboard"),
    path('select_primary_warehouse', select_primary_warehouse, name='select_primary_warehouse'),
    path('dashboard/datatable/<item_name>/<department_name>', dashboard_datatable, name="dashboard_server_side_table"),

]