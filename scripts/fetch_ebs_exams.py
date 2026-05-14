#!/usr/bin/env python3
"""
Scrape all Korean History exam PDFs from EBS and save to data/raw/history_exam/.

Directory layout:
  data/raw/history_exam/{exam_no}/  (e.g. 74/)
    {exam_no}회_심화_문제지.pdf
    {exam_no}회_심화_답지.pdf
    {exam_no}회_기본_문제지.pdf
    {exam_no}회_기본_답지.pdf
"""

import os
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://www.ebs.co.kr"
LIST_URL = (
    "https://www.ebs.co.kr/pass/examination/history/infomation/problem"
    "?c.page={page}&catgrySno=29&searchConditionCondition=0&searchCondition="
    "&searchKeywordCondition=0&pstMtrdYn=N&searchKeyword=&bbsId=547&"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Referer": "https://www.ebs.co.kr/",
}
TOTAL_PAGES = 6
DELAY = 0.5  # seconds between requests

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "history_exam"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def download_file(url: str, dest: Path) -> bool:
    if dest.exists():
        print(f"    skip (exists): {dest.name}")
        return False
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as r:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(r.read())
        print(f"    saved: {dest.name} ({dest.stat().st_size // 1024} KB)")
        return True
    except Exception as e:
        print(f"    ERROR downloading {url}: {e}")
        return False


def parse_exam_no(title: str) -> str | None:
    """Extract exam number like '74' from titles such as '제74회' or '74회'."""
    m = re.search(r"(\d+)회", title)
    return m.group(1) if m else None


def parse_level(filename: str) -> str:
    """Return '심화' or '기본' based on filename."""
    if "심화" in filename:
        return "심화"
    if "기본" in filename or "초급" in filename:
        return "기본"
    return "기타"


def parse_doc_type(filename: str) -> str:
    if "문제" in filename:
        return "문제지"
    if "답" in filename:
        return "답지"
    return "기타"


def scrape_post(post_id: str) -> list[dict]:
    """Return list of {url, filename} for all attachments in a post."""
    url = f"{BASE_URL}/pass/examination/history/infomation/problem/{post_id}?p="
    html = fetch(url)
    time.sleep(DELAY)

    # Get post title
    title_m = re.search(r"<div[^>]*class=\"con_txt\"[^>]*>\s*(.*?)\s*</div>", html, re.S)
    title = title_m.group(1).strip() if title_m else ""
    title = re.sub(r"<[^>]+>", "", title).strip()

    exam_no = parse_exam_no(title)

    # Find all attachment links
    attachments = re.findall(
        r'<a href="(https://n-osp\d+\.ebs\.co\.kr/storage/post/[^"]+)"[^>]*>([^<]+)</a>',
        html,
    )

    results = []
    for dl_url, raw_name in attachments:
        name = urllib.parse.unquote(raw_name.replace("&#40;", "(").replace("&#41;", ")").strip())
        # Fall back to parsing exam number from filename if title didn't have it
        eno = exam_no or parse_exam_no(name)
        if not eno:
            print(f"  skip (no exam no): {name}")
            continue
        results.append({"post_id": post_id, "exam_no": eno, "title": title,
                        "url": dl_url, "raw_name": name})
    return results


def main():
    import urllib.parse  # noqa: PLC0415 (needed for unquote)

    print(f"Output directory: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: collect all post IDs across all pages
    all_post_ids: list[str] = []
    for page in range(1, TOTAL_PAGES + 1):
        print(f"Scanning list page {page}/{TOTAL_PAGES}...")
        html = fetch(LIST_URL.format(page=page))
        ids = re.findall(r'/pass/examination/history/infomation/problem/(\d+)\?p=', html)
        # deduplicate while preserving order
        for pid in ids:
            if pid not in all_post_ids:
                all_post_ids.append(pid)
        time.sleep(DELAY)

    print(f"\nFound {len(all_post_ids)} posts total.\n")

    # Step 2: visit each post and download attachments
    stats = {"downloaded": 0, "skipped": 0, "errors": 0}
    for i, post_id in enumerate(all_post_ids, 1):
        print(f"[{i}/{len(all_post_ids)}] Post {post_id}")
        try:
            attachments = scrape_post(post_id)
        except Exception as e:
            print(f"  ERROR fetching post {post_id}: {e}")
            stats["errors"] += 1
            continue

        if not attachments:
            print("  no attachments found")
            continue

        for att in attachments:
            exam_no = att["exam_no"] or "unknown"
            level = parse_level(att["raw_name"])
            doc_type = parse_doc_type(att["raw_name"])
            filename = f"{exam_no}회_{level}_{doc_type}.pdf"
            dest = OUTPUT_DIR / exam_no / filename

            ok = download_file(att["url"], dest)
            if ok:
                stats["downloaded"] += 1
            else:
                stats["skipped"] += 1
            time.sleep(DELAY)

    print(f"\nDone. Downloaded: {stats['downloaded']}, Skipped: {stats['skipped']}, Errors: {stats['errors']}")


if __name__ == "__main__":
    import urllib.parse
    main()
