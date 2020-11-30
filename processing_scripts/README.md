In this directory are all of the scripts, including now-obsolete or one-off ones, used for processing, analyzing, and ablating the Pile.

## Replication

Replication scripts are listed in approximate order needed for replication.

 - `pass2_shuffle_holdout.py`: Script for pass 2 of the shuffling. The first pass is handled in Pile repo if `--interleave` is used. Pass 2 is basically going through each of the interleaved outputs and shuffling it. For more info on why this works see https://blog.janestreet.com/how-to-shuffle-a-big-dataset/. This step also creates the holdout set, from which val and test are created.
 - `dedupe_train.py`: This script removes all exact-match data in the held-out sets (including test and val) from the training set. This is very important because otherwise there's leakage between train and val/test. Fuzzy matching is out of the scope of this script.

## Analysis & Ablation

 - `lang_len_analysis.py`: Runs analysis for length in {chars, bytes, tokens, words} and language. Saves the result as .jsonl.zst files which need a second pass to aggregate, but this first pass is the more expensive one anyways, and this means we can make nice histograms and stuff. Should be run with `TOKENIZERS_PARALLELISM=false` for max performance since it prevents thread thrashing. This script would be a useful template for other future analysis.
 - `ablation_dedupe/make_excludes_lambada_wikitext.py`: For ablation; detokenizes LAMBADA and wikitext in preparation for eval-dedupe. Thie script should be obsolete now; `write_out.py` in lm_evaluation_harness handles many more sets. TODO: write detailed guide on how to use `write_out.py`
 - `ablation_dedupe/make_deduped.py`: For ablation; performs decontamination of training data against validation/test data. Run `make_excludes_lambada_wikitext` or `write_out.py` first. TODO: clean up and make official validation-dedupe script.

## Miscellaneous

 - `repack_arxiv.py`: packages the arxiv tar.gz into a lmd archive.
 - `pile_proportions_sanitycheck.py`: shows the proportions of a sample of a Pile output to make sure the proportions are about right
 - `github_reduce.py`: One off script for cutting down github to a manageable size. Pile repo used to pull all 600GB of github each time but that's kinda ridiculous since we only use 95GB of it.
 - `join.py`: Script for joining multiple lmd archives. Much faster than actually using lmd because we're not actually parsing the json.
 - `fix_empty_lines.py`: One-off script for fixing extra newlines in lmd archives. Shouldn't be too useful for replication but included for completeness.