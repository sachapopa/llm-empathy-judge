import json
import pandas as pd
import anthropic
from dotenv import load_dotenv

MODEL = "claude-haiku-5-5"
PROMPT_FILE = "prompts/emotional_reactions_v2.txt"
MECHANISM = "level_emr"
N_PILOT = 20
RAW_FILE = "data/raw_pilot_v2.jsonl"
SEED = 42


def load_items(mechanism, n):
    """Evaluation items for one mechanism, with texts and human level."""
    # 1. read sample.csv; keep rows where split is 'evaluations' AND mechanism matches
    # 2. merge with clean.csv on rp_id (you only need rp_id, seeker_post, response_post)
    # 3. draw n rows reproducibly (.sample with SEED)
    sample = pd.read_csv("data/sample.csv")
    clean = pd.read_csv("data/clean.csv")
    mask = (sample["split"] == "evaluations") & (sample["mechanism"] == mechanism)
    filtered = sample[mask]
    merged = filtered.merge(clean[['rp_id', 'seeker_post', 'response_post']], on="rp_id", validate='one_to_one')
    items = merged.sample(n, random_state=SEED)
    return items

def build_prompt(template, seeker_post, response):
    """Put the post and reply into the template."""
    filled = template.replace("{seeker_post}", seeker_post)
    filled = filled.replace("{response}", response)
    
    return filled

# ---- plumbing (written for you) -------------------------------------
def call_judge(client, prompt):
    """Send one prompt to the model; return the reply text and token usage."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=200,          # the JSON answer is short; caps cost if it rambles
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "disabled"}

    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return text, response.usage


def save_raw(rp_id, text, usage):
    """Append one raw reply to a file BEFORE any parsing, so nothing is lost."""
    record = {
        "rp_id": rp_id,
        "text": text,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "thinking_tokens": usage.output_tokens_details.thinking_tokens,

    }
    with open(RAW_FILE, "a") as f:          # "a" = append, never overwrite
        f.write(json.dumps(record) + "\n")  # one JSON object per line
# ----------------------------------------------------------------------


def parse(text):
    """Return (rating, reason) from the judge's JSON reply, or (None, None) if it fails."""
    try:
        result = json.loads(text)
        return  result['rating'], result['reason']
    except (json.JSONDecodeError, KeyError):
        return None, None
        

def main():
    load_dotenv()
    client = anthropic.Anthropic()
    template = open(PROMPT_FILE).read()
    items = load_items(MECHANISM, N_PILOT)
    results = []
    # loop over the items' rows:
    for _, row in items.iterrows():
    #   build the prompt, call the judge, save raw, parse,
        prompt = build_prompt(template, row['seeker_post'], row['response_post'])
        text, usage = call_judge(client, prompt)
        save_raw(row['rp_id'], text, usage)
    #   add a dict of rp_id, human level, judge rating, reason to results
        rating, reason = parse(text)
        record = {
            "rp_id": row['rp_id'], 
            "human_level": row['level'],
            "judge_rating": rating,
            "judge_reason": reason
        }
        results.append(record)
    # turn results into a DataFrame, print it, save to data/pilot_results.csv
    df = pd.DataFrame(results)
    print(df)
    df.to_csv('data/pilot_results.csv', index=False)

if __name__ == "__main__":
    main()