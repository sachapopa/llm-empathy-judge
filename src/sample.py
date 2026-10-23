import pandas as pd

MECHANISMS = ['level_emr', 'level_exr', 'level_inr']
LEVELS = [0, 1, 2]
N_EXAMPLES = 2
N_EVAL = 50
SEED = 42


def draw(df, mechanism, level):
    """Return a small table of N_FEWSHOT + N_EVAL replies at this level
    for this mechanism, with columns rp_id, mechanism, level, split."""
    # 1. keep only rows where this mechanism's column equals this level
    mask = df[mechanism] == level
    # 2. draw N_FEWSHOT + N_EVAL of them reproducibly (.sample, random_state=SEED)
    subset = df[mask].sample(N_EXAMPLES + N_EVAL, random_state=SEED)
    # 3. keep just the rp_id column
    piece = subset[['rp_id']]
    # 4. add columns: mechanism, level, split
    piece['mechanism'] = mechanism
    piece['level'] = level
    #    split = 'fewshot' for the first N_FEWSHOT rows, 'eval' for the rest
    piece['split'] = ['examples'] * N_EXAMPLES + ['evaluations'] * N_EVAL
    return piece


def main():
    df = pd.read_csv('data/clean.csv')
    pieces = []
    # loop over MECHANISMS, and inside that over LEVELS:
    for mechanism in MECHANISMS:
        for level in LEVELS:
    #     call draw(...) and add the result to pieces
            piece = draw(df, mechanism, level)
            pieces.append(piece)
    sample = pd.concat(pieces, ignore_index = True)
    print(len(sample))
    print(sample.head())
    print(sample['split'].value_counts())
    print(pd.crosstab(sample['mechanism'], sample['level']))
    sample.to_csv('data/sample.csv', index=False)
    


if __name__ == "__main__":
    main()