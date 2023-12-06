import glob
import json
import os
from datetime import datetime
from typing import List

from openpyxl import load_workbook


def split_list(lst, n):
    """将列表lst拆分成n个元素的子列表"""
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def create_expense_ledger(
        invoice_list: List[dict], claimant: str = "报销人",
        save_path: str = "费用报销台账.xlsx", excel_template: str = "templates"):
    """
    创建费用报销台账

    :param invoice_list: 发票信息列表，列表内字典应包含以下字段
        'date': 发票日期
        'id': 发票号码
        'money': 发票金额
    :param claimant: 报销人
    :param save_path: 费用报销台账存储路径
    :param excel_template: excel 模板文件夹路径
    """

    # 以 11行 为限值抽取发票信息
    for index, inv_list in enumerate(split_list(invoice_list, 12)):
        wb = load_workbook(filename=os.path.join(excel_template, '费用报销台账.xlsx'))
        sheet_ranges = wb['费用报销台账']
        for r_index, info in enumerate(inv_list):
            if r_index + 1 <= 12:
                sheet_ranges.cell(row=r_index + 4, column=1).value = r_index + 1  # 序号
                sheet_ranges.cell(row=r_index + 4, column=2).value = f"{info['date'][:4]}.{info['date'][4:6]}.{info['date'][6:]}"   # 日期
                # sheet_ranges.cell(row=r_index + 4, column=3).value = ""     # 事由
                sheet_ranges.cell(row=r_index + 4, column=4).value = "电子发票"  # 发票类型 []
                sheet_ranges.cell(row=r_index + 4, column=5).value = info['id']  # 发票号码(8位)
                sheet_ranges.cell(row=r_index + 4, column=6).value = info['money']  # 发票金额
                sheet_ranges.cell(row=r_index + 4, column=7).value = claimant  # 报销人
                # sheet_ranges.cell(row=r_index + 4, column=8).value = ""     # 备注

        wb.save(save_path if len(
            invoice_list) == 1 else f"{os.path.splitext(save_path)[0]}_{index}{os.path.splitext(save_path)[1]}")


if __name__ == '__main__':
    invoice_list = []
    for json_path in glob.glob("../data/json/*.json"):
        with open(json_path, "r", encoding="utf-8") as f:
            invoice_dict = json.loads("".join(f.readlines()))
            invoice_list.append({
                "date": str(invoice_dict["invoice_info"]["date"]),
                "id": invoice_dict["invoice_info"]["id"],
                "code": invoice_dict["code"],
                "money": invoice_dict["invoice_info"]["total"],
            })

    invoice = invoice_list[0]
    invoice_list = [invoice for _ in range(21)]

    create_expense_ledger(
        invoice_list,
        claimant="测试人",
        save_path="../费用报销台账.xlsx", excel_template="../templates"
    )
