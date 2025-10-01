import pytest
from app.utils.convert_docx import convert_docx
import os


def test_convert_docx():
    print("\n\n#### test convert docx ####\n\n")

    file_path = "./test_docx_1.docx"
    abs_path = os.path.abspath(os.path.dirname(__file__)) + "/" + file_path

    print(convert_docx(file_path=abs_path))