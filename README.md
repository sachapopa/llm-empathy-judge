# Can an LLM judge rate empathy like trained annotators?

This is a project looking at LLM-as-judge evaluations on mental-health support replies compared to human ratings. Data come from the EPITOME Reddit dataset. The evaluation framework is based on EPITOME's three empathy mechanisms: emotional reactions, explorations and interpretations (Sharma et al., 2020). The goal of the project was to determine to what extent LLM evaluations agree with human raters and if different prompt styles (i.e. giving worked examples) can improve agreement. 

## Key findings
- Agreement with human annotators was closest for emotional reactions (κ = 0.63, approaching the human–human κ = 0.69) and lowest for interpretations and explorations (κ = 0.41–0.44).
- Errors were systematic and differed by mechanism: the judge was too lenient on emotional reactions at level 0, too strict on strong explorations (3/50 rated 2), and too lenient on weak interpretations (24/50 rated 2).
- Adding six randomly selected human-rated examples to the prompt did not detectably change agreement for any mechanism (κ differences −0.07 to +0.02; all 95% bootstrap CIs include zero), while increasing input tokens about 2.5×.
- The full study (≈860 judge calls) cost about $0.2 in API fees.

## Question

LLM judges could help reduce costs of evaluating mental-health AI. This project explored to what extent LLM-as-judge evaluations of mental health support agree with trained human raters and whether agreement can be increased by providing the judge with worked examples. 

## Data

Data come from the EPITOME Reddit dataset, which gathered help seeking posts on mental health subreddits and responses these received. Trained crowdworkers evaluated responses on the EPITOME empathy framework, rating each response from levels 0-2 on emotional reactions, interpretation, exploration. These measure the extent to which responses communicate an emotional reaction to the post, interpret the seeker's experience, and explore the seeker's experience, respectively (Sharma et al., 2020). 
- Cleaning: clean.py loads the data, finds and drops conflicting or duplicated replies. Each file had 61 repeating rows. 19 replies had inconsistent ratings in at least one file and were dropped from all three. The other repeats were kept with one copy (final n = 3004 replies)
- Sample: sample.py draws 50 evaluations and 2 examples (seed 42) sampled independently per level and per mechanisms (468 rows, 450 evaluations + 18 examples; 52 per mechanism × level). 

## Method
- Judge: Claude Haiku 5.5 (claude-haiku-5-5) via the Anthropic API was used; thinking was disabled, the API does not accept temperature. Judge outputted one rating per item per condition as a JSON of its reason and rating. Output tokens were capped at 300. There were 0 parse failures. 
- Prompts: Prompts included short description of judge's task and the definitions from EPITOME. Condition A contained definitions only; Condition B is identical to A plus it added 6 random examples (2 per level). Examples came from a held-out set.   
- Pilot: A pilot was carried out to test the prompting. I tested 20 items on emotional reactions and 13/20 (65%) matched the human judgements. 3/7 disagreements were related to the judge reading "I'm sorry" as not an explicit expression of emotion. This was addressed in v2 of the prompt and pilot was rerun (16/20 matched). The pilot items were excluded from analysis. Explorations and interpretations got a 5-item format check, with no prompt changes, therefore the items were kept in the full analysis. 
- Analysis: exact agreement, Cohen's κ (unweighted and quadratic), confusion matrices, paired bootstrap CIs (1,000 resamples)

## Results

| Mechanism | Condition | n | Exact agreement | κ | κ (quadratic) |
|---|---|---|---|---|---|
| Emotional reactions | A | 130 | 0.75 | 0.63 | 0.75 |
| Emotional reactions | B | 130 | 0.75 | 0.62 | 0.76 |
| Explorations | A | 150 | 0.63 | 0.44 | 0.44 |
| Explorations | B | 150 | 0.58 | 0.37 | 0.41 |
| Interpretations | A | 150 | 0.61 | 0.41 | 0.59 |
| Interpretations | B | 150 | 0.62 | 0.43 | 0.57 |

Human–human agreement in the original annotation: κ = 0.69 (Sharma et al., 2020).
Comparisons with humans use unweighted κ. The benchmark is approximate: it was computed between annotator pairs on the natural (imbalanced) data and averaged across mechanisms, whereas these figures compare the judge with the dataset label on a balanced sample.

- Emotional reactions came closer to the human benchmark (0.63 vs 0.69), but explorations and interpretations are clearly lower (0.41–0.44).
- Adding six randomly selected human-rated examples to the prompt did not detectably change agreement for any mechanism (κ differences −0.07 to +0.02; all 95% bootstrap CIs include zero), while increasing input tokens about 2.5×.

## What the errors show

### Emotional Reactions 

LLM judge overrated level 0 (15 of 44 replies the annotators rated 0 were given a 1). It might be that the LLM judge counts implicit warmth (casual friendliness) that the annotators didn’t treat as an emotional reaction. After the v2 prompt, explicit sympathy ("I'm sorry...") was handled well, with 35/45 level-2 replies correct.

### Explorations

LLM judge under-rates strong explorations, with only 3 of 50 level-2 replies rated as 2 (34 got a 1 and 13 a 0). It appeared that the judge sets a high bar for what counts as "specific" question. It also may discount questions that are embedded in larger responses. 

### Interpretations

LLM judge over-rates weak interpretations (24 of 50 level-1 replies were rated 2). This appears to be because the paper’s definition says that describing a similar experience counts as strong, and the judge applies that literally to any self-disclosure, while the annotators often rated loosely related experiences as weak. 

### Human-label inconsistency 

Some human ratings were inconsistent. For example, two similar replies saying the responder was "in the same boat" as the seeker were rated 0 and 2 for emotional reactions by annotators. LLM judge gave both a 1. Therefore, some disagreements between LLM and humans might be due to noise in human annotation, not judge errors. 

## Limitations

- Balanced sample: equal numbers per level mean overall agreement doesn’t reflect real-world prevalence, where level 0 dominates. Per-level results are the more informative part.
- Crowdworker labels as reference: the annotators were trained crowdworkers, not clinicians or people with lived experience, and agreed with each other at only κ = 0.69. Disagreement with the reference isn’t always a judge error.
- Random examples in condition B: a few randomly drawn examples were somewhat inconsistent with the rubric’s edge cases, which may explain why examples didn’t help. Expert-chosen examples might behave differently.
- Single-turn context: the judge and annotators see one post and one reply; some replies are ambiguous without the wider conversation.
- One model and one language tested: results are for Claude Haiku 5.5 in English only, and may not generalise to other models or languages.
- One rating per item: the judge isn’t deterministic (one pilot item flipped between runs), and run-to-run variability wasn’t measured. 
- only the emotional-reactions prompt was refined after a pilot, which may favour it in the comparison between mechanisms.


## Next steps

- perform a multilingual analysis between English and Romanian to test if agreement lowers. 
- calculate judge reliability and calibration by running the judge several times over the same items. 
- running a multi-turn context analysis.
- using chosen rather than random worked examples. 

## Reproducing

Requirements: Python 3.12 and the packages in `requirements.txt`
(`pip install -r requirements.txt`), plus an Anthropic API key.

1. Download the three Reddit CSVs from the
   [EPITOME repository](https://github.com/behavioral-data/Empathy-Mental-Health)
   (`emotional-reactions-reddit.csv`, `interpretations-reddit.csv`,
   `explorations-reddit.csv`) into `data/`. The data is released under an academic licence.
2. Create a `.env` file in the project root containing `ANTHROPIC_API_KEY=your-key`.
   It is gitignored and must never be committed.
3. Run the scripts in order from the project root:
   - `python src/clean.py`: removes duplicates and conflicting ratings, writes `data/clean.csv`
   - `python src/sample.py`: draws the balanced sample (seed 42), writes `data/sample.csv`
   - `python src/judge.py`: runs the LLM judge for conditions A and B; resumes if interrupted
   - `python src/analyse.py`: computes agreement, confusion matrices and bootstrap CIs into `results/`

Total API cost for a full run was about $0.2 using Claude Haiku 5.5.

## Repository structure

    prompts/    judge prompts per mechanism and condition (A: rubric only, B: with examples)
    src/        pipeline scripts (clean, sample, judge, analyse)
    results/    aggregate results: summary table, confusion matrices, pilot item IDs
    notes.md    decisions and findings log
    data/       not included: raw data, sample, judge outputs (contain Reddit text)

## Ethics and data

The data are real posts from people seeking mental-health support. To protect them,
this repository contains no posts, replies, or judge outputs quoting them: only code,
prompts, reply IDs and aggregate statistics. Examples in this README are paraphrased.
The dataset is used under its academic licence; please cite the original work:

Sharma, A., Miner, A. S., Atkins, D. C., & Althoff, T. (2020). A computational approach
to understanding empathy expressed in text-based mental health support. *EMNLP 2020*.


