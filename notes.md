## Data cleaning (19.10.2026)

**Findings**
- Each file has 3,084 rows and 3,023 unique replies. 
- 61 extra rows per file are repeated replies (59 pairs + 1 triple)
- Most repeats look like double annotation with same text and almost identical rationale highlights
- Some repeats disagree on empathy rating: 10 in emotional reactions, 10 in interpretations and 5 in exolorations. 
There are 19 independent repeats in any file. 

**Decisions**
- Removed 19 conflicting replies from all three files. 
- Kept one copy for other repeats. 

