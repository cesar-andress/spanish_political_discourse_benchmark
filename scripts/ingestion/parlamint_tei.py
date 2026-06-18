"""Parse local ParlaMint TEI/XML (and optional plain-text exports)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterator, Mapping, Optional
from xml.etree import ElementTree as ET

TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"tei": TEI_NS}
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

SOURCE_URL = "https://www.clarin.si/repository/xmlui/handle/11356/2004"
CHAIR_LABEL = "Presidencia"


def _tag(local: str) -> str:
    return f"{{{TEI_NS}}}{local}"


def _local_name(element: ET.Element) -> str:
    tag = element.tag
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _person_display_name(person: ET.Element) -> str:
    name = person.find("tei:persName", NS)
    if name is None:
        return person.get(XML_ID, "unknown")
    parts = [name.findtext("tei:forename", default="", namespaces=NS)]
    parts.extend(surname.text for surname in name.findall("tei:surname", NS) if surname.text)
    return " ".join(part for part in parts if part).strip() or person.get(XML_ID, "unknown")


def _org_label(org: ET.Element) -> str:
    names = org.findall("tei:orgName", NS)
    for name in names:
        if name.get("full") == "abb" and (name.text or "").strip():
            return name.text.strip()
    for name in names:
        if (name.text or "").strip():
            return name.text.strip()
    return org.get(XML_ID, "unknown").replace("party.", "")


def load_person_registry(path: Path) -> Dict[str, Dict[str, str]]:
    root = ET.parse(path).getroot()
    registry: Dict[str, Dict[str, str]] = {}
    for person in root.findall(".//tei:person", NS):
        person_id = person.get(XML_ID)
        if not person_id:
            continue
        party_ref = "unknown"
        for affiliation in person.findall("tei:affiliation", NS):
            if affiliation.get("role") == "member" and (affiliation.get("ref") or "").startswith("#party."):
                party_ref = affiliation.get("ref", "unknown").lstrip("#")
                break
        registry[f"#{person_id}"] = {
            "speaker_name": _person_display_name(person),
            "party_ref": party_ref,
        }
    return registry


def load_org_registry(path: Path) -> Dict[str, str]:
    root = ET.parse(path).getroot()
    registry: Dict[str, str] = {}
    for org in root.findall(".//tei:org", NS):
        org_id = org.get(XML_ID)
        if org_id:
            registry[f"#{org_id}"] = _org_label(org)
    return registry


def resolve_party(party_ref: str, org_registry: Mapping[str, str]) -> str:
    if party_ref in org_registry:
        return org_registry[party_ref]
    if party_ref.startswith("party."):
        return party_ref.split(".", 1)[-1]
    return party_ref or "unknown"


def _session_date(root: ET.Element, file_path: Path) -> str:
    for xpath in (
        ".//tei:profileDesc/tei:settingDesc/tei:setting/tei:date[@when]",
        ".//tei:sourceDesc//tei:date[@when]",
        ".//tei:titleStmt/tei:meeting[@n][@ana]",
    ):
        node = root.find(xpath, NS)
        if node is not None and node.get("when"):
            return node.get("when", "")[:10]
        if node is not None and node.get("n") and re.fullmatch(r"\d{4}-\d{2}-\d{2}", node.get("n", "")):
            return node.get("n", "")
    match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
    return match.group(1) if match else "1970-01-01"


def _utterance_speaker(u_elem: ET.Element, person_registry: Mapping[str, Mapping[str, str]]) -> tuple[str, str]:
    who = u_elem.get("who")
    if who and who in person_registry:
        entry = person_registry[who]
        return entry["speaker_name"], entry["party_ref"]
    ana = u_elem.get("ana", "")
    if "#chair" in ana:
        return CHAIR_LABEL, "non_partisan"
    if who:
        return who.lstrip("#"), "unknown"
    return "unknown", "unknown"


def _extract_seg_text(seg: ET.Element) -> str:
    chunks: list[str] = []
    if seg.text:
        chunks.append(seg.text)
    for child in seg:
        if _local_name(child) in {"gap", "note", "incident", "kinesic", "vocal"}:
            if child.tail:
                chunks.append(child.tail)
            continue
        if child.text:
            chunks.append(child.text)
        if child.tail:
            chunks.append(child.tail)
    return "".join(chunks)


def extract_utterance_text(u_elem: ET.Element) -> str:
    parts = [_extract_seg_text(seg) for seg in u_elem.findall("tei:seg", NS)]
    text = " ".join(part.strip() for part in parts if part and part.strip())
    return re.sub(r"\s+", " ", text).strip()


def parse_tei_session(
    file_path: Path,
    *,
    person_registry: Mapping[str, Mapping[str, str]],
    org_registry: Mapping[str, str],
    source_url: str = SOURCE_URL,
) -> Iterator[Dict[str, Any]]:
    root = ET.parse(file_path).getroot()
    session_date = _session_date(root, file_path)
    file_id = root.get(XML_ID) or file_path.stem

    for u_elem in root.findall(".//tei:u", NS):
        text = extract_utterance_text(u_elem)
        if not text:
            continue
        utterance_id = u_elem.get(XML_ID) or f"{file_id}.u"
        speaker_name, party_ref = _utterance_speaker(u_elem, person_registry)
        speaker_party = resolve_party(party_ref, org_registry)

        yield {
            "document_id": utterance_id,
            "source_type": "parliamentary",
            "source_name": "ParlaMint",
            "date": session_date,
            "speaker_name": speaker_name,
            "speaker_party": speaker_party,
            "language": "es",
            "text": text,
            "provenance": {
                "source_url": source_url,
                "license_status": "to_be_verified",
                "source_file": file_path.name,
            },
        }


def parse_plain_text_export(file_path: Path, *, source_url: str = SOURCE_URL) -> Iterator[Dict[str, Any]]:
    """Fallback for ParlaMint .txt exports (one speech per blank-line block)."""
    session_date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
    session_date = session_date_match.group(1) if session_date_match else "1970-01-01"
    blocks = re.split(r"\n\s*\n", file_path.read_text(encoding="utf-8"))
    for index, block in enumerate(blocks):
        text = re.sub(r"\s+", " ", block.strip())
        if not text:
            continue
        yield {
            "document_id": f"{file_path.stem}-txt-{index:04d}",
            "source_type": "parliamentary",
            "source_name": "ParlaMint",
            "date": session_date,
            "speaker_name": "unknown",
            "speaker_party": "unknown",
            "language": "es",
            "text": text,
            "provenance": {
                "source_url": source_url,
                "license_status": "to_be_verified",
                "source_file": file_path.name,
            },
        }


def iter_parlamint_files(input_path: Path) -> Iterator[Path]:
    if input_path.is_file():
        yield input_path
        return
    patterns = ("*.xml", "*.txt")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(input_path.rglob(pattern))
    for path in sorted(set(files)):
        name = path.name.lower()
        if "listperson" in name or "listorg" in name or "taxonomy" in name:
            continue
        if name.endswith(".ana.xml"):
            continue
        yield path
