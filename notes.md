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

## Drawing data (23.10.2026)

- Drew 50 evaluations samples and 2 examples (seed 42) sampled independently per level and per mechanisms. (468 rows, 450 evaluations + 18 examples (52 per mechanism × level).
- Drew equal number of responses because levels are unequal in dataset. This means the overall performance in this sample is different than real-world overall performance, which is weighted by how often each level appears.   
Responses might repeat between mechanisms, but each mechanism is rated separately.  


## Pilot results (27.10.2026)

- API does not accept a temperature parameter; judge runs at default sampling settings. Each item judged once per condition.
- Emotional reactions pilot: 13/20 (65%) mathched the human judgements. 3/7 disagreements were related to the judge reading "I'm sorry" as not an explicit expression of emotion. This was addressed in v2 of the prompt and pilot was rerun (16/20 matched). All disagreements were off by only one; humans gave two similar responses 0 and 2 (dam1f5h and dvd5jcq)
- human and LLM judges only see one post and response, and some are hard to judge out of context, making multi-turn interaction evaluations important

## Results - two conditions (28.10.2026)
- A small, cheap LLM judge approaches human-level agreement on emotional reactions, but has systematic, mechanism-specific biases (too strict on strong explorations, too lenient on weak interpretations), and adding randomly chosen worked examples didn’t help, while more than doubling the cost.