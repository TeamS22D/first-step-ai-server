from typing import List, Union
from pydantic import BaseModel
import mistune

# --- Node Models ---
class TextNode(BaseModel):
    type: str = "text"
    text: str


class ListItemNode(BaseModel):
    type: str = "list_item"
    children: List["MarkdownNode"]


class ListNode(BaseModel):
    type: str = "list"
    ordered: bool = False
    children: List[ListItemNode]


class HeadingNode(BaseModel):
    type: str = "heading"
    level: int
    children: List[TextNode]


class ParagraphNode(BaseModel):
    type: str = "paragraph"
    children: List["MarkdownNode"]


class CodeBlockNode(BaseModel):
    type: str = "code_block"
    language: str
    code: str


class LinkNode(BaseModel):
    type: str = "link"
    url: str
    children: List["MarkdownNode"]


class ImageNode(BaseModel):
    type: str = "image"
    url: str
    alt: str


MarkdownNode = Union[
    HeadingNode,
    ListNode,
    ListItemNode,
    TextNode,
    ParagraphNode,
    CodeBlockNode,
    LinkNode,
    ImageNode,
]


class Document(BaseModel):
    name: str
    nodes: List[MarkdownNode]


