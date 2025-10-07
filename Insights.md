# VU Amsterdam Metaphor Corpus: Overview and some Insights

## Introduction

The VU Amsterdam Metaphor Corpus (VUAMC) is the only publicly available resource that provides access to more than 25,000 metaphorical lexical units, all annotated according to an explicit and replicable procedure. The corpus was constructed by selecting four samples of approximately 47,000 words each from the BNC-Baby (together totaling about 186,000 words). Each lexical unit in these samples was manually annotated for metaphor following the Metaphor Identification Procedure Vrije Universiteit (MIPVU). In total, the corpus contains 186,688 words. This project attempts to deconstruct the corpus, extract its data, and prepare it for further computational processing.

## The VUAMC XML

The VUAMC, distributed by the Oxford Text Archive as a TEI P5 XML file, brings together annotated fragments from the BNC-Baby across four registers: **academic, news, fiction, and conversation**. The archive consists primarily of one master XML file (`VUAMC.xml`) accompanied by TEI schemas (`VUAMC.odd`, `VUAMC.rng`, `VUAMC.rnc`) and a catalogue header.

- Each fragment appears as a `<text>` element identified by a unique `xml:id` (e.g. `a1e-fragment01`, `b17-fragment02`).  
- Linguistic content is structured hierarchically: `<body>` → `<div1>` → `<p>`/`<head>` → `<s>` (sentences).  
- `<w>` elements represent word tokens and `<c>` elements punctuation, each word carrying attributes for lemma and POS (CLAWS tags).  
- Metaphor annotation is encoded by `<seg>` elements layered over tokens:  
  - `function="mrw"` marks metaphor-related words, with optional `@subtype` (e.g. WIDLII, PP).  
  - Multi-word metaphors use `xml:id` on the first element and `@corresp` on followers.  
  - `function="mFlag"` marks metaphor signals (lexical, phrasal, morphological).  

Register distinctions are mapped externally by fragment identifiers.

## Parsing and Token Counts

Parsing the XML with a custom parser yields:

1. Collapses MWEs using anchor–follower IDs.  
2. Excludes `<seg function="trunc">` and POS `PUN`.  
3. Normalises possessive `'s`.  
4. Assigns pseudo-sentence IDs for tokens outside `<s>`.  

### Results

- Raw `<w>` tokens: **205,115**  
- After processing: **188,120 lexical units**  
- Metaphor-related units: **25,447**  
- Published reference: **186,695 words**  

### Register-Level Counts

| Register     | Tokens (Book) | Tokens (Parser) | Δ Tokens | MRWs (Book) | MRWs (Parser) | Δ MRWs | MRW % (Book) | MRW % (Parser) | MRW Δ    %    |
|--------------|----------------|-----------------|----------|-------------|---------------|--------|---------------|----------------|-----------------|
| Academic     | 49,314         | 49,681          | + 367 | 9,120       | 9,073         | –47    | 18.5%         |  18.3%|  - 0.2% |
| News         | 44,792         | 45,118          | +326     | 7,342       | 7,312         | –30    | 16.4%         | 16.2%          | - 0.2% |
| Fiction      | 44,648         | 44,893          | +245     | 5,293       | 5,251         | –42    |  11.9% | 11.7%          | - 0.2% |
| Conversation | 47,934         | 48,398          | +464     | 3,687       | 3,676         | –11    | 7.7%          | 7.6%           | - 0.1% |
| **Total**    | **186,688**    | **188,090**     | **+1,402** | **25,442** | **25,312** |  **–130** | **13.6%** |  **13.5%** | **- 0.1%** |

## Inconsistent Numbers

- Parsing the untrimmed `b1g-fragment02` yields 20,151 lexical units (vs. 3,006 reported), but only 633 MRWs. The discrepancy arises because unannotated sentences remain in the OTA XML. When trimmed to the authoritative ranges (s738–765, s1012, s1299, s1401, s1485–1584), the count drops to 3,156 lexical units—preserving 633 MRWs and reducing total corpus size closer to the official figure.

- Metaphorical status of “of”: In the News register, 125 MRWs with lemma = “of” are dropped as potential noise from formulaic constructions.

## Output File

The parser outputs `VUAMC.csv` with one row per lexical unit. Columns:

| Column        | Description                                | Example                  |
|---------------|--------------------------------------------|--------------------------|
| File_ID       | VUAMC text identifier                      | a1e-fragment01           |
| Genre         | Register of the text                       | Academic; News; Fiction  |
| Sentence_ID   | Sentence label                             | a1e-fragment01_s23       |
| Original_Word | Surface form                               | approach; stirred up     |
| Lemma         | Lemmatized form(s)                         | approach; stir up        |
| POS           | Part-of-speech tag(s); merged for MWEs     | NN1; VVD+AVP             |
| Metaphor      | Marks metaphor-related words               | mrw; [blank]             |
| Type/Subtype  | Metaphor categories and subcategories      | met/WIDLII; met/PP       |
| MFlag         | Metaphor signal flag                       | lex; phrase; morph       |
| xml:id        | Anchor ID for MRW span                     | a1e-fragment01-pv4       |
| corresp       | Follower pointer linking to anchor         | #a1e-fragment01-pv4      |

## License

The VU Amsterdam Metaphor Corpus (VUAMC) is distributed by the **Oxford Text Archive** under the **Creative Commons Attribution–NonCommercial 4.0 International License (CC BY-NC 4.0)**.

This permits use, distribution, and adaptation for non-commercial research and education, provided appropriate credit is given. Commercial use is not allowed.


## Author
Developed and maintained as part of ongoing research on metaphor annotation and analysis in the VUAMC at Erfurt Univeristy.

[Daban Q. Jaff] (2025). VU Amsterdam Metaphor Corpus Parser. Available at: https://github.com/dabjaff/VU-Amsterdam-Metaphor-Corpus-Parser
