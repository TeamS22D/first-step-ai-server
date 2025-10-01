from docx import Document


def convert_docx(file_path: str):
    document = Document(file_path)
    text_content = []
    for para in document.paragraphs:
        text_content.append(para.text)

    return '\n'.join(text_content)
