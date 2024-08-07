import os

from PyQt5.QtWidgets import QVBoxLayout, QFileDialog

from util import pltUtil
from util.readwelllogdata import read_las_file


def Select_multiple_files():
    # print(dataAll["welllog"]['T001'][0:1])
    file_paths, _ = QFileDialog.getOpenFileNames(None, "选择文件", "/",
                                                 "Excel文件 (*.xlsx *xls);;Word文件 (*.docx)")
    if file_paths:
        print(file_paths)


def Select_welllog_files(self):
    """
    导入测井数据
    :param self:
    :return:
    """
    file_paths, _ = QFileDialog.getOpenFileNames(self, "选择文件", "/",
                                                 "Well log(LAS) (*.las)")

    welllog = {}
    for i, fp in enumerate(file_paths):
        print(os.path.basename(fp).split('.')[0])
        wellName = os.path.basename(fp).split('.')[0]
        welllog[wellName] = read_las_file(fp)

    # dataAll["welllog"] = welllog
    if file_paths:
        print(file_paths)
