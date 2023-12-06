import json
import glob
from typing import List

import openpyxl

from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, Protection
from openpyxl.styles import numbers


def create_expense_ledger(invoice_list: List[dict], claimant: str = "报销人", save_path: str = "费用报销台账.xlsx"):
    """
    创建费用报销台账

    :param invoice_list: 发票信息列表，列表内字典应包含以下字段
        'date': 发票日期
        'id': 发票号码
        'code': 发票代码
        'money': 发票金额
    :param claimant: 报销人
    :param save_path: 费用报销台账存储路径
    """
    wb = openpyxl.Workbook()    # 创建一个新的工作簿对象
    ws = wb.active  # 获取工作表对象(sheet)
    ws.title = '费用报销台账'    # 设置Sheet名称
    
    title = ws.cell(row=1, column=1, value='费用报销台账')
    title.font = Font(name=u'宋体', size=20)
    title.alignment = Alignment(horizontal='center', vertical='center')
    ws.merge_cells('A1:H1')

    wb.save(save_path)


if __name__ == '__main__':
    invoice_list = []
    for json_path in glob.glob("../data/json/*.json"):
        with open(json_path, "r", encoding="utf-8") as f:
            invoice_dict = json.loads("".join(f.readlines()))
            invoice_list.append({
                "date": invoice_dict["invoice_info"]["date"],
                "id": invoice_dict["invoice_info"]["id"],
                "code": invoice_dict["code"],
                "money": invoice_dict["invoice_info"]["total"],
            })

    create_expense_ledger(invoice_list, "./费用报销台账.xlsx")
