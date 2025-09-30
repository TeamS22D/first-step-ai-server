import pytest
from app.services.openai_file import get_openai_file
from pprint import pprint
import os


def test_openai_file():
    file_path = "test_pdf_1.pdf"
    abs_path = os.path.abspath(os.path.dirname(__file__)) + "/" + file_path

    response = get_openai_file(file_path=abs_path, file_name=file_path)

    pprint(response.output_text)