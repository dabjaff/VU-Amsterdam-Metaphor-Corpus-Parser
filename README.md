# VUAMC → ALL.csv Parser

This script converts the **VU Amsterdam Metaphor Corpus (VUAMC)** XML file into a flat CSV file (`ALL.csv`). It reproduces the agreed parsing rules precisely, including special handling for the **b1g** file.

---

## What it does
- Parses the VUAMC XML into a structured CSV.
- Merges multi‑word expressions (MWEs) using `<seg function="mrw">` with `xml:id`/`corresp` references.
- Normalizes segmented MWEs (suffixes like `s1`, `s2`, `s3` are collapsed).
- Applies genre labels based on file ID prefixes.
- Skips punctuation tokens (`POS == PUN`).
- Skips truncations marked as `<seg function="trunc">`.
- **Special case for `b1g`:**
  - Only parses sentences **738–765, 1012, 1299, 1401, and 1485–1584**.
  - Skips all other b1g sentences and *all* tokens outside `<s>`.

---

## Input
- **XML file:** A TEI XML file of the VUAMC (default path is set to your Desktop).

---

## Output
- **CSV file:** `ALL.csv` written to the same folder as the XML file.
- Includes these columns:
  - `File_ID`
  - `Genre`
  - `Sentence_ID`
  - `Original_Word`
  - `Lemma`
  - `POS`
  - `Metaphor`
  - `Type`
  - `Subtype`
  - `MFlag`
  - `xml:id`
  - `corresp`

---

## Usage
```bash
# Run with explicit XML path
python Parser_no_b1g_trim.py "/path/to/VUAMC.xml"

# Or rely on the default path inside the script
python Parser_no_b1g_trim.py
```

---

## Dependencies
- Python 3.8+
- [pandas](https://pandas.pydata.org/)
- [lxml](https://lxml.de/)

Install dependencies if needed:
```bash
pip install pandas lxml
```

---

## Notes
- The script was written for **reproducibility** and mirrors the agreed parsing logic exactly.
- A checksum (MD5 + SHA256) of the output CSV is printed at the end for verification.
- The print statement `"Daban: Welcome to Vuamc world and enjoy Metaphors!"` is preserved for continuity with earlier runs.

---

## Author
Developed and maintained as part of ongoing research on metaphor annotation and analysis in the VUAMC at Erfurt Univeristy.

