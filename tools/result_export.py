import glob
import json
import os
import shutil

from time import strftime, localtime
import logging

import numpy as np

from tools.logging_utils import log_set
from tools.QRcode_decode import decode_single_path
from tools.img_utils import base64_to_image_raw
from tools.tax_url_decode import get_verify_img, verify_info_exits, get_standard_tax_filename
from tools.excel_template import create_expense_ledger_xlsx, create_expense_voucher_xlsx, create_meal_expense_docx, \
    create_invoice_verification_docx


def get_invoice_lst(json_path: str) -> list:
    invoice_list = []
    for path in glob.glob(os.path.join(json_path, "*.json")):
        with open(path, "r") as json_f:
            invoice_dict = json.loads("".join(json_f.readlines()))
            invoice_list.append({
                "date": str(invoice_dict["invoice_info"]["date"]),
                "id": invoice_dict["invoice_info"]["id"],
                "code": invoice_dict["code"],
                "money": invoice_dict["invoice_info"]["total"],
                "money_before_taxes": invoice_dict["invoice_info"]["money"],
                "img_b64": invoice_dict["verify_info"]["img_b64"],
            })
    return invoice_list


def export_tree_build(claimant: str, export_path: str = "./"):
    """构建导出文件夹树"""
    data_str = strftime("%Y.%m", localtime())
    main_path = os.path.join(export_path, f"{claimant}{data_str}")
    fp_path = os.path.join(main_path, "发票")
    os.makedirs(main_path, exist_ok=True)
    os.makedirs(fp_path, exist_ok=True)
    return data_str, main_path, fp_path


def export_main(claimant: str, json_path: str, export_path: str = "./"):
    # 构建文件树并创建对应文件夹
    data_str, main_path, fp_path = export_tree_build(claimant=claimant, export_path=export_path)

    # 构建输出报表
    invoice_lst = get_invoice_lst(json_path=json_path)
    # create expense ledger xlsx / 费用报销台账.xlsx
    create_expense_ledger_xlsx(
        invoice_list=invoice_lst,
        claimant=claimant,
        save_path=os.path.join(main_path, f"费用报销台账-{claimant}{data_str}.xlsx"),
        xlsx_template="templates"
    )

    # create invoice verification docx / 发票真伪查询.docx
    create_invoice_verification_docx(
        invoice_list=invoice_lst,
        save_path=os.path.join(main_path, f"发票真伪查询-{claimant}{data_str}.docx")
    )

    # create meal expense docx / 工作餐费报销明细表.docx
    create_meal_expense_docx(
        invoice_list=invoice_lst,
        claimant=claimant,
        save_path=os.path.join(main_path, f"工作餐费报销明细表-{claimant}{data_str}.docx"),
        docx_template="templates"
    )

    # create expense voucher xlsx / 现金支出面单.xlsx
    create_expense_voucher_xlsx(
        invoice_list=invoice_lst,
        claimant=claimant,
        save_path=os.path.join(main_path, f"现金支出面单-{claimant}{data_str}.xlsx"),
        xlsx_template="templates"
    )

    # 复制对应PDF
    for tax_info in invoice_lst:
        target_pdf_name = f"{tax_info['date'][0:4]}.{tax_info['date'][4:6]}.{tax_info['date'][6:8]}-{tax_info['money_before_taxes']}.pdf"
        shutil.copy(os.path.join("cache/pdf", target_pdf_name),
                    os.path.join(fp_path, target_pdf_name.replace(str(tax_info['money_before_taxes']), str(int(tax_info["money"])))))


def main_verify_img():
    for path in glob.glob("C:/Users/18201/Desktop/发票/*pdf"):
        invoice_msg = decode_single_path(path)
        print(invoice_msg)
        if not verify_info_exits(invoice_msg, "cache"):
            get_verify_img(invoice_msg)
        os.makedirs("cache/pdf", exist_ok=True)
        export_filename = get_standard_tax_filename(path, export_path="cache/pdf")
        shutil.copy(path, export_filename)


if __name__ == '__main__':
    log_set(log_level=logging.INFO)
    export_main(claimant="王一", json_path="cache/json/for_Wang", export_path="export")
    export_main(claimant="苏二", json_path="cache/json/for_Su", export_path="export")
