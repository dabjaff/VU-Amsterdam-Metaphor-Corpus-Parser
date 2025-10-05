# VUAMC → VUAMC.csv Parser

This script converts the **VU Amsterdam Metaphor Corpus (VUAMC)** XML file into a flat CSV file (`VUAMC.csv`). It reproduces the agreed parsing rules precisely, including special handling for the **b1g** file.

---

## What it does
- Parses the VUAMC XML into a structured CSV.
- Merges multi-word expressions (MWEs) using `<seg function="mrw">` with `xml:id`/`corresp` references.
- Normalizes segmented MWEs (suffixes like `s1`, `s2`, `s3` are collapsed).
- Applies genre labels based on file ID prefixes.
- Skips punctuation tokens (`POS == PUN`).
- Skips truncations marked as `<seg function="trunc">`.
- **Special case for `b1g`:**
  - Only parses sentences **738–765, 1012, 1299, 1401, and 1485–1584**.
  - Skips all other `b1g` sentences and *all* tokens outside `<s>`.
- **News**: Excludes **125** tokens with lemma `of` that are annotated as metaphorical in VUAMC from MRW counts (treated as potential annotation noise).


---

## Input
- **XML file:** A TEI XML file of the VUAMC(https://ota.bodleian.ox.ac.uk/repository/xmlui/handle/20.500.12024/2541?show=full) (default path is set to your Desktop).

---

## Output
- **CSV file:** `VUAMC.csv` written to the same folder as the XML file.
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
- After running the script, you will be You will be greeted by  `"Daban: Welcome to Vuamc world and enjoy Metaphors!"`.

---

## Author
Developed and maintained as part of ongoing research on metaphor annotation and analysis in the VUAMC at Erfurt Univeristy.

[Daban Q. Jaff] (2025). VU-Amsterdam-Metaphor-Corpus-Unveiled.
Available at: [github.com/dabjaff/VU-Amsterdam-Metaphor-Corpus-Unveiled]

