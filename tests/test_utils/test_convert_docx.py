import pytest
from app.utils.convert_docx import *
from pprint import pprint
import os


def test_convert_docx():
    print("\n\n#### test convert docx ####\n\n")

    file_path = "./test_docx_1.docx"
    abs_path = os.path.abspath(os.path.dirname(__file__)) + "/" + file_path

    print(convert_docx(file_path=abs_path))

def test_convert_docx_table():
    print("\n\n#### test convert docx ####\n\n")

    file_path = "./test_docx_2.docx"
    abs_path = os.path.abspath(os.path.dirname(__file__)) + "/" + file_path

    pprint(convert_docx_table(file_path=abs_path))

def test_parse_list():
    print("\n\n#### test parse list ####\n\n")

    file_path = "./test_docx_1.docx"
    abs_path = os.path.abspath(os.path.dirname(__file__)) + "/" + file_path

    pprint(parse_styles(file_path=abs_path))

    file_path = "./test_docx_2.docx"
    abs_path = os.path.abspath(os.path.dirname(__file__)) + "/" + file_path

    pprint(parse_styles(file_path=abs_path))