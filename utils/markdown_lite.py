"""Minimal Markdown renderer for the in-app documentation viewer.

Supports only the constructs used by the docs/ folder: headings, fenced code,
tables, blockquotes, ordered and unordered lists, inline code, bold, italic,
links, and horizontal rules. Standard library only, so no new dependency.
"""

from __future__ import annotations

import html
import re

_FENCE = re.compile(r"^```(\w*)\s*$")
_HEADING = re.compile(r"^(#{1,4})\s+(.*)$")
_LIST_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
_RULE = re.compile(r"^-{3,}\s*$")
_MD_LINK = re.compile(r"\]\(\.?/?([\w\-]+)\.md(#[^)]*)?\)")


def _slug(text: str) -> str:
    """Approximate GitHub heading anchors."""
    text = re.sub(r"[`*_]", "", text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"\s+", "-", text)


def _rewrite_links(text: str) -> str:
    """Point .md links at the in-app viewer instead of raw files."""

    def replace(match):
        anchor = match.group(2) or ""
        return f"](/docs/{match.group(1)}{anchor})"

    return _MD_LINK.sub(replace, text)


def _inline(text: str) -> str:
    """Format inline markup in text that is already HTML-escaped."""
    spans: dict[str, str] = {}

    def stash(match):
        key = f"\x00{len(spans)}\x00"
        spans[key] = f"<code>{match.group(1)}</code>"
        return key

    text = re.sub(r"`([^`]+)`", stash, text)
    text = _rewrite_links(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)

    for key, value in spans.items():
        text = text.replace(key, value)

    return text


def _table(block: list[str]) -> str:
    rows = []
    for line in block:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)

    if len(rows) >= 2 and all(re.fullmatch(r":?-{2,}:?", c or "") for c in rows[1]):
        header, body = rows[0], rows[2:]
    else:
        header, body = None, rows

    def cells_html(cells, tag):
        return "".join(
            f"<{tag}>{_inline(html.escape(cell))}</{tag}>" for cell in cells
        )

    out = ["<div class='table-wrap'><table>"]
    if header:
        out.append(f"<thead><tr>{cells_html(header, 'th')}</tr></thead>")
    out.append("<tbody>")
    for row in body:
        out.append(f"<tr>{cells_html(row, 'td')}</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _collect_list(lines: list[str], start: int) -> tuple[list[dict], int]:
    """Read list items, folding indented continuation lines into their item."""
    items: list[dict] = []
    i = start

    while i < len(lines):
        match = _LIST_ITEM.match(lines[i])
        if not match:
            break

        indent = len(match.group(1))
        marker, text = match.group(2), match.group(3)
        i += 1

        # Continuation lines belong to this item when they are indented deeper.
        while i < len(lines):
            candidate = lines[i]
            if not candidate.strip():
                look = i + 1
                while look < len(lines) and not lines[look].strip():
                    look += 1
                if look >= len(lines):
                    break
                next_line = lines[look]
                deeper = len(next_line) - len(next_line.lstrip()) > indent
                if _LIST_ITEM.match(next_line) or deeper:
                    i = look
                    continue
                break

            if _LIST_ITEM.match(candidate):
                break

            if len(candidate) - len(candidate.lstrip()) > indent:
                text = f"{text} {candidate.strip()}"
                i += 1
                continue

            break

        items.append({"indent": indent, "marker": marker, "text": text})

    return items, i


def _render_list_tree(nodes: list[dict]) -> str:
    """Render sibling nodes, grouping runs of the same list type."""
    parts: list[str] = []
    index = 0

    while index < len(nodes):
        ordered = nodes[index]["marker"][0].isdigit()
        tag = "ol" if ordered else "ul"
        parts.append(f"<{tag}>")

        while index < len(nodes) and nodes[index]["marker"][0].isdigit() == ordered:
            node = nodes[index]
            parts.append(f"<li>{_inline(html.escape(node['text']))}")
            if node["children"]:
                parts.append(_render_list_tree(node["children"]))
            parts.append("</li>")
            index += 1

        parts.append(f"</{tag}>")

    return "".join(parts)


def _nest_items(items: list[dict]) -> list[dict]:
    """Turn a flat item list into a tree based on indentation."""
    root: list[dict] = []
    stack: list[tuple[int, list[dict]]] = [(-1, root)]

    for item in items:
        while len(stack) > 1 and stack[-1][0] >= item["indent"]:
            stack.pop()
        node = {"marker": item["marker"], "text": item["text"], "children": []}
        stack[-1][1].append(node)
        stack.append((item["indent"], node["children"]))

    return root


def _list_block(lines: list[str], start: int) -> tuple[str, int]:
    items, next_index = _collect_list(lines, start)
    return _render_list_tree(_nest_items(items)), next_index


def render(markdown: str) -> str:
    """Convert the docs markdown subset into HTML."""
    lines = markdown.splitlines()
    out: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        fence = _FENCE.match(line.strip())
        if fence:
            language = fence.group(1)
            i += 1
            buffer = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buffer.append(lines[i])
                i += 1
            i += 1
            code = html.escape("\n".join(buffer))
            attr = f" data-lang='{language}'" if language else ""
            out.append(f"<pre{attr}><code>{code}</code></pre>")
            continue

        if not line.strip():
            i += 1
            continue

        heading = _HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            out.append(
                f"<h{level} id='{_slug(title)}'>"
                f"{_inline(html.escape(title))}</h{level}>"
            )
            i += 1
            continue

        if _RULE.match(line.strip()):
            out.append("<hr>")
            i += 1
            continue

        if line.strip().startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            out.append(_table(block))
            continue

        if line.strip().startswith(">"):
            quoted = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quoted.append(re.sub(r"^\s*>\s?", "", lines[i]).strip())
                i += 1
            body = _inline(html.escape(" ".join(q for q in quoted if q)))
            out.append(f"<blockquote>{body}</blockquote>")
            continue

        if _LIST_ITEM.match(line):
            rendered, i = _list_block(lines, i)
            out.append(rendered)
            continue

        paragraph = []
        while i < len(lines):
            current = lines[i]
            if not current.strip():
                break
            if (
                _FENCE.match(current.strip())
                or _HEADING.match(current)
                or _RULE.match(current.strip())
                or current.strip().startswith(("|", ">"))
                or _LIST_ITEM.match(current)
            ):
                break
            paragraph.append(current.strip())
            i += 1
        out.append(f"<p>{_inline(html.escape(' '.join(paragraph)))}</p>")

    return "\n".join(out)
