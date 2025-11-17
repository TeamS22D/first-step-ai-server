import mistune
from app.schemas.document import *


def _flatten_children(nodes: List[MarkdownNode]) -> List[MarkdownNode]:
    """문단(ParagraphNode)이나 리스트 내부의 불필요한 중첩을 평탄화."""
    flat = []
    for n in nodes:
        if isinstance(n, ParagraphNode):
            flat.extend(_flatten_children(n.children))
        else:
            flat.append(n)
    return flat



def parse_node(node: dict) -> MarkdownNode:
    node_type = node["type"]

    if node_type == "text":
        return TextNode(text=node.get("raw", ""))

    elif node_type == "heading":
        children = [parse_node(child) for child in node.get("children", [])]
        level = node.get("attrs", {}).get("level", 1)
        return HeadingNode(level=level, children=[c for c in _flatten_children(children) if isinstance(c, TextNode)])

    elif node_type == "paragraph":
        children = [parse_node(child) for child in node.get("children", [])]
        return ParagraphNode(children=_flatten_children(children))

    elif node_type == "list":
        items = [parse_node(child) for child in node.get("children", []) if child["type"] == "list_item"]
        return ListNode(ordered=node.get("attrs", {}).get("ordered", False), children=items)

    elif node_type == "list_item":
        children = [parse_node(child) for child in node.get("children", [])]
        return ListItemNode(children=_flatten_children(children))

    elif node_type == "block_code":
        lang = node.get("attrs", {}).get("info", "")
        return CodeBlockNode(language=lang, code=node.get("raw", ""))

    elif node_type == "image":
        url = node.get("attrs", {}).get("url", "")
        alt = node.get("attrs", {}).get("alt", "")
        return ImageNode(url=url, alt=alt)

    elif node_type == "link":
        url = node.get("attrs", {}).get("url", "")
        children = [parse_node(child) for child in node.get("children", [])]
        # flatten paragraphs/images/text
        return LinkNode(url=url, children=_flatten_children(children))

    else:
        # fallback
        if "children" in node:
            children = [parse_node(child) for child in node["children"]]
            return ParagraphNode(children=_flatten_children(children))
        return TextNode(text=node.get("raw", f"[Unknown type: {node_type}]"))


def parse_document(markdown_text: str, name: str) -> Document:
    markdown = mistune.create_markdown(renderer="ast")
    ast = markdown(markdown_text)
    nodes = [parse_node(node) for node in ast]
    return Document(name=name, nodes=nodes)
