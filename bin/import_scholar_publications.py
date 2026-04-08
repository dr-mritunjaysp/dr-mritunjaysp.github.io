#!/usr/bin/env python

import re
import sys
from datetime import datetime
from pathlib import Path

import bibtexparser
import yaml
from scholarly import scholarly


ROOT = Path(__file__).resolve().parent.parent
SOCIALS_FILE = ROOT / "_data" / "socials.yml"
BIB_FILE = ROOT / "_bibliography" / "papers.bib"


def safe_print(message: str) -> None:
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "replace").decode("ascii"))


def normalize_title(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def load_scholar_user_id() -> str:
    with SOCIALS_FILE.open("r", encoding="utf-8") as handle:
        socials = yaml.safe_load(handle) or {}
    scholar_userid = socials.get("scholar_userid", "").strip()
    if not scholar_userid:
        raise ValueError("Missing scholar_userid in _data/socials.yml")
    return scholar_userid


def load_existing_entries():
    with BIB_FILE.open("r", encoding="utf-8") as handle:
        bib_db = bibtexparser.load(handle)

    titles = {}
    keys = {entry["ID"] for entry in bib_db.entries if entry.get("ID")}
    for entry in bib_db.entries:
        title = entry.get("title", "")
        if title:
            titles[normalize_title(title)] = entry

    return bib_db.entries, titles, keys


def unique_key(base_key: str, used_keys: set[str]) -> str:
    candidate = base_key
    suffix = 2
    while candidate in used_keys:
        candidate = f"{base_key}{suffix}"
        suffix += 1
    used_keys.add(candidate)
    return candidate


def make_key(title: str, year: str, used_keys: set[str]) -> str:
    words = re.findall(r"[a-z0-9]+", title.lower())
    short_title = "".join(words[:3]) or "publication"
    base_key = f"peelam{year}{short_title}"
    return unique_key(base_key, used_keys)


def extract_venue(citation: str, volume: str, number: str, pages: str, year: str) -> str:
    venue = citation.strip()
    if not venue:
        return ""

    venue = re.sub(rf",\s*{re.escape(str(year))}\s*$", "", venue).strip()
    if volume and number and pages:
        venue = re.sub(
            rf"\s+{re.escape(str(volume))}\s*\({re.escape(str(number))}\),\s*{re.escape(str(pages))}\s*$",
            "",
            venue,
        ).strip()
    elif volume and pages:
        venue = re.sub(rf"\s+{re.escape(str(volume))},\s*{re.escape(str(pages))}\s*$", "", venue).strip()
    elif pages:
        venue = re.sub(rf",\s*{re.escape(str(pages))}\s*$", "", venue).strip()

    return venue


def bibtex_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def format_field(name: str, value: str, multiline: bool = False) -> str:
    if multiline:
        return f"  {name:<15}= {{{value}}},"
    return f"  {name:<15}= {{{value}}},"


def build_entry(pub: dict, used_keys: set[str]) -> str | None:
    bib = pub.get("bib", {})
    title = (bib.get("title") or "").strip()
    if not title:
        return None

    year = str(bib.get("pub_year") or "Unknown")
    author = (bib.get("author") or "").strip()
    volume = str(bib.get("volume") or "").strip()
    number = str(bib.get("number") or "").strip()
    pages = str(bib.get("pages") or "").strip().replace("-", "--")
    abstract = (bib.get("abstract") or "").strip()
    citation = (bib.get("citation") or "").strip()
    pub_url = (pub.get("pub_url") or "").strip()
    author_pub_id = (pub.get("author_pub_id") or "").strip()
    google_scholar_id = author_pub_id.split(":", 1)[1] if ":" in author_pub_id else author_pub_id
    venue = extract_venue(citation, volume, number, pages, year)

    entry_key = make_key(title, year, used_keys)
    lines = [f"@article{{{entry_key},"]
    lines.append(format_field("title", bibtex_escape(title)))
    if author:
        lines.append(format_field("author", bibtex_escape(author)))
    if venue:
        lines.append(format_field("journal", bibtex_escape(venue)))
    if volume:
        lines.append(format_field("volume", bibtex_escape(volume)))
    if number:
        lines.append(format_field("number", bibtex_escape(number)))
    if pages:
        lines.append(format_field("pages", bibtex_escape(pages)))
    if year and year != "Unknown":
        lines.append(format_field("year", bibtex_escape(year)))
    lines.append(format_field("bibtex_show", "true"))
    if pub_url:
        lines.append(format_field("html", bibtex_escape(pub_url)))
    if google_scholar_id:
        lines.append(format_field("google_scholar_id", bibtex_escape(google_scholar_id)))
    if abstract:
        lines.append(format_field("abstract", bibtex_escape(abstract), multiline=True))
    lines.append("}")
    return "\n".join(lines)


def main() -> int:
    scholar_userid = load_scholar_user_id()
    existing_entries, existing_titles, used_keys = load_existing_entries()

    safe_print(f"Fetching publications for Google Scholar ID: {scholar_userid}")
    author = scholarly.fill(scholarly.search_author_id(scholar_userid), sections=["publications"])
    publications = author.get("publications", [])

    new_entries = []
    for publication in publications:
        filled_publication = scholarly.fill(publication)
        title = (filled_publication.get("bib", {}).get("title") or "").strip()
        if not title:
            continue

        normalized_title = normalize_title(title)
        if normalized_title in existing_titles:
            safe_print(f"Skipping existing: {title}")
            continue

        entry = build_entry(filled_publication, used_keys)
        if entry:
            new_entries.append(entry)
            safe_print(f"Prepared: {title}")

    if not new_entries:
        safe_print("No new publications found to import.")
        return 0

    with BIB_FILE.open("a", encoding="utf-8") as handle:
        handle.write(
            "\n\n% Imported from Google Scholar on "
            + datetime.now().strftime("%Y-%m-%d")
            + "\n\n"
            + "\n\n".join(new_entries)
            + "\n"
        )

    safe_print(f"Added {len(new_entries)} new publications to {BIB_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
