import json
import pandas as pd
import anthropic
from dotenv import load_dotenv
import os

MODEL = "claude-haiku-5-5"
PROMPTS_A = {
    "level_emr": "prompts/emotional_reactions_v2_A.txt",
    "level_exr": "prompts/explorations_v1_A.txt",
    "level_inr": "prompts/interpretations_v1_A.txt",
}
PROMPTS_B = {
    "level_emr": "prompts/emotional_reactions_v2_B.txt",
    "level_exr": "prompts/explorations_v1_B.txt",
    "level_inr": "prompts/interpretations_v1_B.txt"
}
SEED = 42

def run_mechanism(client, mechanism, condition):
    """Runs loading of items, building prompt and calls agent per mechanism."""
    raw_path = f"data/raw_{condition}_{mechanism}.jsonl"
    prompts = PROMPTS_A if condition == "A" else PROMPTS_B 
    template = open(prompts[mechanism]).read()
    items = load_items(mechanism)
    if condition == "B":
        examples_text=format_examples(load_items(mechanism, split='examples'))
    else:
        examples_text = ""
    if mechanism == "level_emr":
    # 1. read pilot_results.csv
        pilot = pd.read_csv("data/pilot_results.csv")
    # 2. take its rp_id column to drop
        pilot = pilot["rp_id"]
    # 3. keep only items whose rp_id is NOT in those 
        mask = ~items['rp_id'].isin(pilot)
        items = items[mask]
    
    results = []
    done = already_done(raw_path)
    # loop over the items' rows:
    for _, row in items.iterrows():
        if row['rp_id'] in done:
            continue
       # build the prompt, call the judge, save raw, parse,
        prompt = build_prompt(template, row['seeker_post'], row['response_post'], examples_text)
        text, usage = call_judge(client, prompt)
        save_raw(row['rp_id'], text, usage, raw_path)
        # add a dict of rp_id, human level, judge rating, reason to results
        rating, reason = parse(text)
        record = {
            "rp_id": row['rp_id'], 
            "human_level": row['level'],
            "judge_rating": rating,
            "judge_reason": reason
            }
        results.append(record)

    df = pd.DataFrame(results)
    print(df)
    df.to_csv(f'data/results_{condition}_{mechanism}.csv', index=False)
    print(mechanism, len(df), "items rated")

def load_items(mechanism, n=None, split='evaluations'):
    """Evaluating items for one mechanism, with texts and human level."""
    sample = pd.read_csv("data/sample.csv")
    clean = pd.read_csv("data/clean.csv")
    mask = (sample["split"] == split) & (sample["mechanism"] == mechanism)
    filtered = sample[mask]
    merged = filtered.merge(clean[['rp_id', 'seeker_post', 'response_post']], on="rp_id", validate='one_to_one')
    if n is not None:
        merged = merged.sample(n, random_state=SEED)
        
    return merged

def format_examples(examples):
    """Return rated examples as a text block"""
    examples = examples.sort_values("level")
    parts = []
    for _, row in examples.iterrows():
        text = f"""<example>
<seeker_post>
{row['seeker_post']}
</seeker_post>
<response>
{row['response_post']}
</response>
<rating>{row['level']}</rating>
</example>"""
        parts.append(text)
    return "\n\n".join(parts)


def build_prompt(template, seeker_post, response, examples_text):
    """Put the post and reply into the template."""
    filled = template.replace("{seeker_post}", seeker_post)
    filled = filled.replace("{response}", response)
    filled = filled.replace("{examples}", examples_text)
    
    return filled

# -----------------------------------------
def already_done(raw_path):
    """Set of rp_ids already saved in this raw file (empty if the file doesn't exist)."""
    if not os.path.exists(raw_path):
        return set()
    with open(raw_path) as f:
        return {json.loads(line)["rp_id"] for line in f}

def call_judge(client, prompt):
    """Send one prompt to the model; return the reply text and token usage."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,          
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "disabled"}

    )
    text = "".join(block.text for block in response.content if block.type == "text")
    return text, response.usage


def save_raw(rp_id, text, usage, file):
    """Append one raw reply to a file BEFORE any parsing, so nothing is lost."""
    record = {
        "rp_id": rp_id,
        "text": text,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "thinking_tokens": usage.output_tokens_details.thinking_tokens,

    }
    with open(file, "a") as f:          # "a" = append, never overwrite
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

    #for mechanism in PROMPTS_A:
        #run_mechanism(client, mechanism, condition="A") 

    for mechanism in PROMPTS_B:
        run_mechanism(client, mechanism, condition="B")

if __name__ == "__main__":
    main()