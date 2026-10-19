import pandas as pd

def load(path):
    """Read one CSV and return a DataFrame."""

    data = pd.read_csv(path)

    return data 

def conflicting_ids(df):
    """Return the set of rp_ids whose copies have different levels."""

    mask = df['rp_id'].duplicated(keep=False)
    dupes = df[mask]
    n_levels = dupes.groupby('rp_id')['level'].nunique()
    conflicts = n_levels[n_levels > 1]

    return set(conflicts.index)

def clean(df, bad_ids):
    """Drop rows whose rp_id is in bad_ids, then drop repeated rp_ids."""

    keep = ~df['rp_id'].isin(bad_ids)
    df = df[keep]
    df = df.drop_duplicates(subset='rp_id')

    return df

def merge_three(emr, exr, inr):
    """One row per reply: rp_id, sp_id, seeker_post, response_post,
    level_er, level_ip, level_ex."""

    basic = emr[['rp_id', 'sp_id', 'seeker_post', 'response_post', 'level']]
    basic = basic.rename(columns={'level': 'level_emr'})

    exr_basic = exr[['rp_id', 'level']].rename(columns={'level': 'level_exr'})
    inr_basic = inr[['rp_id', 'level']].rename(columns={'level': 'level_inr'})

    merged = basic.merge(exr_basic, on='rp_id', validate='one_to_one')
    merged = merged.merge(inr_basic, on='rp_id', validate='one_to_one')

    return merged

def main():
    # load the three files
    emr = load('data/emotional-reactions-reddit.csv')
    exr = load('data/explorations-reddit.csv')
    inr = load('data/interpretations-reddit.csv')
    # union of conflicting ids from all three
    bad_ids = conflicting_ids(emr) | conflicting_ids(exr) | conflicting_ids(inr)
    # clean each file
    emr_clean = clean(emr, bad_ids)
    exr_clean = clean(exr, bad_ids)
    inr_clean = clean(inr, bad_ids)
    print(len(emr_clean), len(exr_clean), len(inr_clean))
    # merge, check (row count, unique ids), save to data/clean.csv
    merged = merge_three(emr_clean, exr_clean, inr_clean)
    print(merged.shape)
    print(merged['rp_id'].is_unique)
    merged.to_csv('data/clean.csv', index=False)


if __name__ == "__main__":
    main()