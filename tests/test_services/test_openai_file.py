import pytest
from app.services.openai_file import *
from pprint import pprint
from docx2pdf import convert
import os


def test_openai_file():
    file_path = "test_pdf_1.pdf"
    abs_path = os.path.abspath(os.path.dirname(__file__)) + "/" + file_path

    response = get_openai_file(file_path=abs_path, file_name=file_path)

    pprint(response.output_text)


def test_process_file():

    pdf_url = "https://drive.usercontent.google.com/u/0/uc?id=12DxPE8qDXGCIDiw8Tn0Is11yBoWVMa0e&export=download"

    response = process_file(file_url=pdf_url)

    pprint(response)


def test_upload_file():
    print("\n\n#### test upload file ####\n\n")

    docx_path = "test_pdf_1.pdf"
    abs_path = os.path.abspath(os.path.dirname(__file__)) + "/" + docx_path
    #
    # convert(docx_path, abs_path)

    response = upload_file(file_url=abs_path)

def test_search_file():
    print("\n\n#### test search file ####\n\n")

    file_id = "file-ArHrn8rx8fRQ6hhpxJrqLp"

    pprint(search_file(file_id=file_id))


def test_file_content():
    print("\n\n#### test file content ####\n\n")

    file_id = "file-QpwQLYWCX4ct3MiRj9VcQk"

    pprint(extract_docx(file_id=file_id))

    ## 파일을 올리는건 가능하지만, 다시 다운로드 할 순 없음
    ## docx는 파일 분석이 불가능 Responses API는 .pdf만 지원
