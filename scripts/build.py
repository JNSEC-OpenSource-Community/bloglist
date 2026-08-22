#!/usr/bin/env python3
"""Build the public XML and OPML files from data/blogs.json.

This script intentionally uses only Python's standard library so that a
beginner can run it without installing a package manager or dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "blogs.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "site"
STYLESHEET = PROJECT_ROOT / "site" / "blogroll.xsl"

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


class ValidationError(Exception):
    """A human-readable input validation error."""


def display_path(path: Path) -> str:
    """Prefer a short path in messages."""

    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def text_value(value: object, field: str, *, required: bool = False) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValidationError(f"{field} 必须是文字（请用双引号包起来）")
    value = value.strip()
    if required and not value:
        raise ValidationError(f"{field} 不能为空")
    return value


def validate_url(value: object, field: str, *, required: bool = False) -> str:
    value = text_value(value, field, required=required)
    if not value:
        return ""
    if any(character.isspace() for character in value):
        raise ValidationError(f"{field} 不能包含空格")

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError(f"{field} 必须是完整网址，例如 https://example.com/")
    return value


def normalized_url(value: str) -> str:
    """Normalize only what is safe for duplicate detection."""

    return value.rstrip("/").lower()


def make_id(name: str, homepage: str, used_ids: set[str]) -> str:
    """Make a stable, non-essential id without asking beginners to invent one."""

    host = urlparse(homepage).netloc.lower().removeprefix("www.")
    base = re.sub(r"[^a-z0-9]+", "-", host).strip("-") or "blog"
    candidate = base
    suffix = 2
    while candidate in used_ids:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used_ids.add(candidate)
    return candidate


def load_and_validate(path: Path) -> tuple[dict, list[dict]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise ValidationError(f"找不到数据文件：{display_path(path)}") from error
    except json.JSONDecodeError as error:
        raise ValidationError(
            f"{display_path(path)} 第 {error.lineno} 行附近的 JSON 格式有误：{error.msg}。"
            "请检查逗号、双引号和大括号。"
        ) from error

    if not isinstance(raw, dict):
        raise ValidationError("最外层必须是一个 JSON 对象，而不是数组或文字")

    version = raw.get("version", 1)
    if version != 1:
        raise ValidationError("version 目前只能填写数字 1")

    title = text_value(raw.get("title"), "title", required=True)
    description = text_value(raw.get("description"), "description", required=True)
    repository = validate_url(raw.get("repository", ""), "repository")

    blogs = raw.get("blogs")
    if not isinstance(blogs, list):
        raise ValidationError("blogs 必须是数组，请使用 [ ] 包住博客条目")

    normalized_blogs: list[dict] = []
    seen_homepages: set[str] = set()
    seen_feeds: set[str] = set()
    used_ids: set[str] = set()

    for index, item in enumerate(blogs, start=1):
        location = f"blogs[{index}]"
        if not isinstance(item, dict):
            raise ValidationError(f"{location} 必须是对象，请使用 {{ }} 包住一条博客")

        name = text_value(item.get("name"), f"{location}.name", required=True)
        homepage = validate_url(
            item.get("homepage"), f"{location}.homepage", required=True
        )
        feed = validate_url(item.get("feed", ""), f"{location}.feed")
        item_description = text_value(
            item.get("description", ""), f"{location}.description"
        )
        language = text_value(item.get("language", ""), f"{location}.language")

        tags = item.get("tags", [])
        if not isinstance(tags, list):
            raise ValidationError(f'{location}.tags 必须是数组，例如 ["编程"]')
        clean_tags: list[str] = []
        for tag_index, tag in enumerate(tags, start=1):
            clean_tag = text_value(tag, f"{location}.tags[{tag_index}]")
            if clean_tag:
                clean_tags.append(clean_tag)

        added_at = text_value(item.get("addedAt", ""), f"{location}.addedAt")
        if added_at:
            try:
                date.fromisoformat(added_at)
            except ValueError as error:
                raise ValidationError(
                    f"{location}.addedAt 必须是 YYYY-MM-DD，例如 2026-01-31"
                ) from error

        custom_id = text_value(item.get("id", ""), f"{location}.id")
        if custom_id:
            if not ID_RE.fullmatch(custom_id):
                raise ValidationError(f"{location}.id 只能包含小写字母、数字和连字符")
            if custom_id in used_ids:
                raise ValidationError(f"{location}.id 与其他条目重复：{custom_id}")
            used_ids.add(custom_id)
        else:
            custom_id = make_id(name, homepage, used_ids)

        homepage_key = normalized_url(homepage)
        if homepage_key in seen_homepages:
            raise ValidationError(f"{location}.homepage 与其他博客重复：{homepage}")
        seen_homepages.add(homepage_key)

        if feed:
            feed_key = normalized_url(feed)
            if feed_key in seen_feeds:
                raise ValidationError(f"{location}.feed 与其他博客重复：{feed}")
            seen_feeds.add(feed_key)

        normalized_blogs.append(
            {
                "id": custom_id,
                "name": name,
                "homepage": homepage,
                "feed": feed,
                "description": item_description,
                "language": language,
                "tags": clean_tags,
                "addedAt": added_at,
            }
        )

    metadata = {
        "version": 1,
        "title": title,
        "description": description,
        "repository": repository,
    }
    return metadata, normalized_blogs


def add_text(parent: ET.Element, tag: str, value: str) -> ET.Element:
    element = ET.SubElement(parent, tag)
    element.text = value
    return element


def build_blogroll_xml(metadata: dict, blogs: list[dict]) -> ET.Element:
    root = ET.Element("blogroll", {"version": str(metadata["version"])})
    add_text(root, "title", metadata["title"])
    add_text(root, "description", metadata["description"])
    if metadata["repository"]:
        add_text(root, "repository", metadata["repository"])

    blogs_element = ET.SubElement(root, "blogs", {"count": str(len(blogs))})
    for blog in blogs:
        blog_element = ET.SubElement(
            blogs_element,
            "blog",
            {
                "id": blog["id"],
                "name": blog["name"],
                "homepage": blog["homepage"],
                "feed": blog["feed"],
                "language": blog["language"],
                "addedAt": blog["addedAt"],
            },
        )
        add_text(blog_element, "description", blog["description"])
        tags_element = ET.SubElement(blog_element, "tags")
        for tag in blog["tags"]:
            add_text(tags_element, "tag", tag)

    return root


def build_opml_xml(metadata: dict, blogs: list[dict]) -> ET.Element:
    root = ET.Element("opml", {"version": "2.0"})
    head = ET.SubElement(root, "head")
    add_text(head, "title", metadata["title"])
    body = ET.SubElement(root, "body")

    for blog in blogs:
        attributes = {
            "text": blog["name"],
            "title": blog["name"],
            "htmlUrl": blog["homepage"],
        }
        if blog["feed"]:
            attributes.update({"type": "rss", "xmlUrl": blog["feed"]})
        ET.SubElement(body, "outline", attributes)

    return root


def xml_text(root: ET.Element, stylesheet: str | None = None) -> str:
    ET.indent(root, space="  ")
    content = ET.tostring(root, encoding="unicode")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    if stylesheet:
        lines.append(f'<?xml-stylesheet type="text/xsl" href="{stylesheet}"?>')
    lines.extend([content, ""])
    return "\n".join(lines)


def write_xml(path: Path, root: ET.Element, stylesheet: str | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml_text(root, stylesheet), encoding="utf-8")


def verify_output(output_dir: Path) -> None:
    files = {
        "blogroll.xml": "blogroll",
        "opml.xml": "opml",
    }
    for filename, expected_root in files.items():
        path = output_dir / filename
        try:
            parsed_root = ET.parse(path).getroot()
        except ET.ParseError as error:
            raise ValidationError(f"生成的 {filename} 不是合法 XML：{error}") from error
        if parsed_root.tag != expected_root:
            raise ValidationError(
                f"生成的 {filename} 根元素应为 <{expected_root}>，实际是 <{parsed_root.tag}>"
            )

    if STYLESHEET.exists():
        try:
            ET.parse(STYLESHEET)
        except ET.ParseError as error:
            raise ValidationError(f"blogroll.xsl 不是合法 XML：{error}") from error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从 JSON 生成带 XSLT 样式的博客列表和 OPML 文件"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="JSON 数据文件（默认：data/blogs.json）",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="输出目录（默认：site）",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="保留该参数以便 GitHub Actions 明确表达‘检查并构建’",
    )
    return parser.parse_args()


def project_relative(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> int:
    args = parse_args()
    input_path = project_relative(args.input)
    output_dir = project_relative(args.output_dir)

    try:
        metadata, blogs = load_and_validate(input_path)
        write_xml(
            output_dir / "blogroll.xml",
            build_blogroll_xml(metadata, blogs),
            stylesheet="blogroll.xsl",
        )
        write_xml(
            output_dir / "opml.xml",
            build_opml_xml(metadata, blogs),
        )
        verify_output(output_dir)
    except (OSError, ValidationError, ValueError) as error:
        print(f"[ERROR] 构建失败：{error}", file=sys.stderr)
        return 1

    print(f"[OK] 已检查 {display_path(input_path)}")
    print(f"[OK] 已生成 {len(blogs)} 个博客条目")
    print(f"[OK] 输出目录：{display_path(output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
