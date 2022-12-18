from openpyxl.styles import PatternFill, Side, Border


def cell_style(cell):
    thin_border = Border(left=Side(style='thin', color='00000000'),
                         right=Side(style='thin', color='00000000'),
                         top=Side(style='thin', color='00000000'),
                         bottom=Side(style='thin', color='FFFFFFFF'))
    cell.fill = PatternFill(start_color="3A3838", end_color="3A3838", fill_type="solid")
    cell.border = thin_border
    if cell.parent.column_dimensions[cell.column_letter].width < len(str(cell.value)):
        cell.parent.column_dimensions[cell.column_letter].width = len(str(cell.value))


def cells_style(sheet, x_max=100, y_max=100):
    for y in range(1, y_max + 20 + 1):
        for x in range(1, max(50, x_max + 1)):
            cell_style(sheet.cell(y, x))
    sheet.sheet_view.zoomScale = 140
