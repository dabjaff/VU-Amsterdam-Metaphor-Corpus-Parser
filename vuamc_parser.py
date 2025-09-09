
from pathlib import Path
import sys
import pandas as pd
import re
import hashlib
from lxml import etree

# ──────────────────────────────────────────────────────────────────────────────
# Paths / Inputs
# If a file is passed on the CLI, use it; otherwise fall back to your desktop
# path. This mirrors the original behavior exactly.
# ──────────────────────────────────────────────────────────────────────────────
if len(sys.argv) > 1:
    XML = Path(sys.argv[1]).expanduser()
else:
    XML = Path("/Users/dabanjaff/Desktop/untitled folder/VUAMC.xml")

OUT_VUAMC = XML.parent / "VUAMC.csv"

# TEI / XML namespaces
NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

# Parsing switches: keep as-is so behavior is unchanged
EXCLUDE_PUNCT = True   # skip tokens if POS == "PUN" (punct mostly encoded as <c/> anyway)
EXCLUDE_TRUNC = True   # skip <seg function="trunc"> tokens entirely

# File ID prefix → genre mapping (VUAMC-specific). This is intentionally hard-
# coded to be explicit and auditable.
prefix_to_genre = {
    "a1e":"News","a1f":"News","a1g":"News","a1h":"News","a1j":"News","a1k":"News","a1l":"News",
    "a1m":"News","a1n":"News","a1p":"News","a1u":"News","a1x":"News","a2d":"News","a31":"News",
    "a36":"News","a38":"News","a39":"News","a3c":"News","a3e":"News","a3k":"News","a3m":"News",
    "a3p":"News","a4d":"News","a5e":"News","a7s":"News","a7t":"News","a7w":"News","a7y":"News",
    "a80":"News","a8m":"News","a8n":"News","a8r":"News","a8u":"News","a98":"News","a9j":"News",
    "aa3":"News","ahb":"News","ahc":"News","ahd":"News","ahe":"News","ahf":"News","ahl":"News",
    "ajf":"News","al0":"News","al2":"News","al5":"News",
    "kb7":"Conversation","kbc":"Conversation","kbd":"Conversation","kbh":"Conversation",
    "kbj":"Conversation","kbp":"Conversation","kbw":"Conversation","kcc":"Conversation",
    "kcf":"Conversation","kcu":"Conversation","kcv":"Conversation",
    "a6u":"Academic","acj":"Academic","alp":"Academic","amm":"Academic","as6":"Academic",
    "b17":"Academic","b1g":"Academic","clp":"Academic","clw":"Academic","crs":"Academic",
    "cty":"Academic","ea7":"Academic","ecv":"Academic","ew1":"Academic","fef":"Academic",
    "ab9":"Fiction","ac2":"Fiction","bmw":"Fiction","bpa":"Fiction","c8t":"Fiction",
    "cb5":"Fiction","ccw":"Fiction","cdb":"Fiction","faj":"Fiction","fet":"Fiction",
    "fpb":"Fiction","g0l":"Fiction",
}

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
_SEG_SUFFIX = re.compile(r"^(?P<root>.+?)(?:s\d+)?$")  # strip trailing s1/s2/s3


def infer_genre(fid: str) -> str:
    """Map file ID to genre; fall back to 'Unknown'."""
    return prefix_to_genre.get((fid or "")[:3].lower(), "Unknown")


def _merge_pipe(a: str, b: str) -> str:
    """Merge two pipe-delimited strings without duplicates, preserving order.
    Useful for Type/Subtype accumulation across MWE parts.
    """
    items, seen = [], set()
    for part in (a, b):
        for tok in [t.strip() for t in str(part).split("|")]:
            if tok and tok.lower() not in seen:
                seen.add(tok.lower())
                items.append(tok)
    return "|".join(items)


def _norm_id(x: str) -> str:
    """Normalize xml:id/corresp by trimming s1/s2/s3 suffixes."""
    if not x:
        return ""
    m = _SEG_SUFFIX.match(x)
    return m.group("root") if m else x

# b1g exception control: keep exactly the windows we settled on
_B1G_ALLOWED_SINGLE = {1012, 1299, 1401}
_B1G_ALLOWED_RANGES = [(738, 765), (1485, 1584)]


def _is_b1g(fid: str) -> bool:
    return (fid or "").lower().startswith("b1g")


def _b1g_sentence_allowed(n_val: int) -> bool:
    if n_val in _B1G_ALLOWED_SINGLE:
        return True
    for lo, hi in _B1G_ALLOWED_RANGES:
        if lo <= n_val <= hi:
            return True
    return False

# ──────────────────────────────────────────────────────────────────────────────
# Row extraction (token level)
# ──────────────────────────────────────────────────────────────────────────────

def extract_row(w, fid, sid, genre):
    """Extract a token row with seg-level MWE support.

    Preference order:
    - if a <seg function='mrw'> is present, use its surface text and metadata;
      record xml:id / corresp on the seg as the anchor/part identifiers;
    - otherwise, fall back to <w> attributes.

    Returns a dict for DataFrame construction, or None if the token should be
    skipped (punctuation or truncation), mirroring original logic.
    """
    # Skip explicit truncations entirely
    if EXCLUDE_TRUNC and w.xpath(".//tei:seg[@function='trunc']", namespaces=NS):
        return None

    lemma = (w.get("lemma") or "").strip()
    pos = (w.get("type") or "").strip()
    if EXCLUDE_PUNCT and pos == "PUN":
        return None

    word_text = (w.text or "").strip()
    met, mtype, msub, mflag = "", "", (w.get("subtype") or "").strip(), ""
    seg_override = None

    # seg-level info (incl. mrw / mFlag)
    seg_anchor_id = ""
    seg_corresp_id = ""

    for seg in w.xpath("tei:seg", namespaces=NS):
        func = (seg.get("function") or "").strip()
        stype = (seg.get("type") or "").strip()
        ssub = (seg.get("subtype") or "").strip()
        if func == "mrw":
            met = "mrw"
            if seg.text:
                seg_override = seg.text.strip() or seg_override
            mtype = _merge_pipe(mtype, stype)
            msub = _merge_pipe(msub, ssub)
            # ids on <seg>
            if not seg_anchor_id:
                seg_anchor_id = (seg.get("{%s}id" % NS["xml"]) or "").strip()
            if not seg_corresp_id:
                seg_corresp_id = (seg.get("corresp") or "").lstrip("#").strip()
        elif func == "mFlag":
            mflag = "mFlag"
            if seg.text:
                seg_override = seg.text.strip() or seg_override
            mtype = _merge_pipe(mtype, stype)
            msub = _merge_pipe(msub, ssub)

    if seg_override:
        word_text = seg_override

    # <w>-level ids (fallbacks)
    w_xmlid = (w.get("{%s}id" % NS["xml"]) or "").strip()
    w_corresp = (w.get("corresp") or "").lstrip("#").strip()

    xmlid = _norm_id(seg_anchor_id or w_xmlid)
    corresp = _norm_id(seg_corresp_id or w_corresp)

    return {
        "File_ID": fid,
        "Genre": genre,
        "Sentence_ID": sid,
        "Original_Word": word_text,
        "Lemma": lemma,
        "POS": pos,
        "Metaphor": met,
        "Type": mtype,
        "Subtype": msub,
        "MFlag": mflag,
        "xml:id": xmlid,
        "corresp": corresp,
    }

# ──────────────────────────────────────────────────────────────────────────────
# Per-sentence merge: stitch MWE parts back onto their anchors
# ──────────────────────────────────────────────────────────────────────────────

def parse_sentence_merge_mwe(s_node, fid, genre, sid):
    """Merge MWE units by normalized xml:id (anchor) and corresp (parts).

    This supports out-of-order parts and intervening tokens. If we encounter a
    part before its anchor, we create a placeholder and fill it when the anchor
    appears.
    """
    rows = []
    anchor_idx = {}

    def promote(anchor_row, part_row):
        # surface
        anchor_row["Original_Word"] = (anchor_row["Original_Word"] + " " + part_row["Original_Word"]).strip()
        # lemma
        if part_row["Lemma"]:
            anchor_row["Lemma"] = (anchor_row["Lemma"] + " " + part_row["Lemma"]).strip()
        # POS
        if part_row["POS"]:
            anchor_row["POS"] = f"{anchor_row['POS']}+{part_row['POS']}" if anchor_row["POS"] else part_row["POS"]
        # annotations (preserve/merge)
        if part_row.get("Metaphor") == "mrw":
            anchor_row["Metaphor"] = "mrw"
        if part_row.get("MFlag") == "mFlag":
            anchor_row["MFlag"] = "mFlag"
        anchor_row["Type"] = _merge_pipe(anchor_row.get("Type", ""), part_row.get("Type", ""))
        anchor_row["Subtype"] = _merge_pipe(anchor_row.get("Subtype", ""), part_row.get("Subtype", ""))

    for w in s_node.xpath(".//tei:w", namespaces=NS):
        r = extract_row(w, fid, sid, genre)
        if r is None:
            continue

        xmlid = _norm_id(r.get("xml:id") or "")
        cor = _norm_id(r.get("corresp") or "")

        # Anchor token: has xmlid but no corresp
        if xmlid and not cor:
            if xmlid in anchor_idx:
                promote(rows[anchor_idx[xmlid]], r)
                rows[anchor_idx[xmlid]]["xml:id"] = xmlid
                rows[anchor_idx[xmlid]]["corresp"] = ""
            else:
                rows.append({**r, "xml:id": xmlid, "corresp": ""})
                anchor_idx[xmlid] = len(rows) - 1
            continue

        # Part token: has corresp (may appear before its anchor)
        if cor:
            if cor in anchor_idx:
                promote(rows[anchor_idx[cor]], r)
            else:
                placeholder = {
                    "File_ID": fid,
                    "Genre": genre,
                    "Sentence_ID": sid,
                    "Original_Word": r["Original_Word"],
                    "Lemma": r["Lemma"],
                    "POS": r["POS"],
                    "Metaphor": r["Metaphor"],
                    "Type": r["Type"],
                    "Subtype": r["Subtype"],
                    "MFlag": r["MFlag"],
                    "xml:id": cor,
                    "corresp": "",
                }
                rows.append(placeholder)
                anchor_idx[cor] = len(rows) - 1
            continue

        # Plain token
        rows.append(r)

    return rows

# ──────────────────────────────────────────────────────────────────────────────
# Whole-corpus parse
# ──────────────────────────────────────────────────────────────────────────────

def parse_xml_to_df(xml_path: Path) -> pd.DataFrame:
    tree = etree.parse(str(xml_path))
    root = tree.getroot()
    texts = root.xpath(".//tei:text[@xml:id]", namespaces=NS)

    out_rows = []
    for text in texts:
        fid = text.get("{%s}id" % NS["xml"])
        genre = infer_genre(fid)

        # Regular sentences
        for s in text.xpath(".//tei:s", namespaces=NS):
            # b1g exception: only allow specified sentence numbers
            if _is_b1g(fid):
                n_attr = s.get("n")
                try:
                    n_val = int(n_attr) if n_attr is not None else None
                except ValueError:
                    n_val = None
                if n_val is None or not _b1g_sentence_allowed(n_val):
                    continue
            sid = f"{fid}_s{s.get('n','')}"
            out_rows.extend(parse_sentence_merge_mwe(s, fid, genre, sid))

        # Tokens outside <s> → nosent buckets
        # For b1g we skip *all* nosent buckets by request
        if not _is_b1g(fid):
            all_w = text.xpath(".//tei:w", namespaces=NS)
            w_in_s = set(text.xpath(".//tei:s//tei:w", namespaces=NS))
            outside = [w for w in all_w if w not in w_in_s]
            if outside:
                count = 0
                for w in outside:
                    count += 1
                    sid = f"{fid}_nosent{count:04d}"
                    bucket = etree.Element("{%s}s" % NS["tei"])  # minimal synthetic sentence
                    bucket.append(w)
                    out_rows.extend(parse_sentence_merge_mwe(bucket, fid, genre, sid))

    df = pd.DataFrame(out_rows)
    # keep only non-empty surface
    df = df[df["Original_Word"].astype(str).str.strip().astype(bool)].copy()
    return df


def md5_sha256(p: Path):
    """Return (md5, sha256) for a file as hex strings."""
    b = p.read_bytes()
    return hashlib.md5(b).hexdigest(), hashlib.sha256(b).hexdigest()


def main():
    if not XML.exists():
        raise SystemExit(f"ERROR: XML not found at {XML}")
    df_all = parse_xml_to_df(XML)
    df_all.to_csv(OUT_VUAMC, index=False)
    md5, sha = md5_sha256(OUT_VUAMC)
    # Keeping the exact print text for compatibility with any downstream logs
    print("Daban: Welcome to Vuamc world and enjoy Metaphors!")
    print("Wrote:", OUT_VUAMC)
    print("Rows:", len(df_all))


if __name__ == "__main__":
    main()
