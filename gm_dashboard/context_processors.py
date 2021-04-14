from gm_dashboard.models import GMSheet
from FnA_dashboard.models import FnaSheet
from utils.department.department_info import read_write_department, Department_Data
import pdb


def gm_sheets(request):
    """
      The context processor must return a dictionary.
    """
    sheets = GMSheet.objects.all()  # query the latest banner image
    return {'gm_sheets': sheets}


def fna_sheets(request):
    """
      The context processor must return a dictionary.
    """
    sheets = FnaSheet.objects.all()  # query the latest banner image
    return {'fna_sheets': sheets}


def sidebar_menu_items(request):
    """
        The context processor must return a dictionary.
    """
    context = {}
    department_name = read_write_department()
    sidebar_data = Department_Data(department_name)
    context["headers"], sidebar_data_content, context["department_name"] = sidebar_data.get_sidebar()

    fna = fna_sheets(request)['fna_sheets']
    gm = gm_sheets(request)['gm_sheets']

    fna_display_name = list(fna.values_list('display_name', flat=True))
    fna_display_name = [x.lower() for x in fna_display_name]

    gm_display_name = list(gm.values_list('display_name', flat=True))
    gm_display_name = [x.lower() for x in gm_display_name]

    for key, data in sidebar_data_content.items():
        final_sidebar = []
        for item in data:
            if item.lower() in fna_display_name:
                fna_item_index = fna_display_name.index(item.lower())
                final_sidebar.append({
                    'id': fna[fna_item_index].id,
                    'display_name': fna[fna_item_index].display_name,
                    'url': '/fna/sheets/' + str(fna[fna_item_index].id),
                })
            elif item.lower() in gm_display_name:
                gm_item_index = gm_display_name.index(item.lower())
                final_sidebar.append({
                    'id': gm[gm_item_index].id,
                    'display_name': gm[gm_item_index].display_name,
                    'url': '/gm/sheets/' + str(gm[gm_item_index].id) + '/summary',
                })
            else:
                final_sidebar.append({
                    'id': 0,
                    'display_name': item,
                    'url': '/fna/sheets/0'
                })
        sidebar_data_content[key] = final_sidebar

    context['sidebar_data'] = sidebar_data_content

    return context
