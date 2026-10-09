# Running the experiment (P03): step-by-step

Everything below uses the **frozen** question set (`data/p02/items_v1.jsonl`, 3,116 questions)
and prompt v001. The run script refuses to start if either has changed.

Each command is **resumable**: if it stops (network, Colab disconnect), run the exact same command
again and it continues where it left off. Failed API calls are logged and retried. They are never
scored.

## The four conditions (arms)

| Arm | What the model sees | Question it answers |
|---|---|---|
| A0 | the question only | What does the model remember? |
| A1 | + 5 passages from the **current** CPIC release | Does up-to-date retrieval help, or hurt "as of an old date" questions? |
| A2 | + 5 passages from **all** releases, unlabelled | A realistic stale or mixed index |
| A3 | + the same passages **labelled with their CPIC versions and dates** | Does version metadata fix version errors? (H2) |

## Part 1: Claude Sonnet 5.5 (on your laptop)

1. Get an API key at console.anthropic.com. A Claude Pro subscription does **not** include API
   access; the API is billed separately.
2. Create the key file (never committed):
   ```bash
   cd ~/pgxtrust
   cp .env.example .env        # then edit .env and paste the key after ANTHROPIC_API_KEY=
   ```
3. Install the SDK and load the key:
   ```bash
   .venv/bin/pip install -e '.[api]'
   set -a; source .env; set +a
   ```
4. **Smoke test first (20 questions, a few cents):**
   ```bash
   .venv/bin/python scripts/p03_run.py --arm A0 --backend claude --limit 20 --tag smoke
   ```
   Check the printed line: `unparseable` should be 0 or close to it, and `errors` should be 0.
   If not, stop and tell Claude before running the full set.
5. Full runs (3,116 questions each):
   ```bash
   for arm in A0 A1 A2 A3; do
     .venv/bin/python scripts/p03_run.py --arm $arm --backend claude
   done
   ```

## Part 2: Llama-3.1-8B-Instruct (Google Colab)

1. On huggingface.co, open `meta-llama/Llama-3.1-8B-Instruct`, accept the licence, then create a
   **read** token (Settings → Access Tokens).
2. In Colab choose Runtime → Change runtime type → a GPU.
   - **Free tier (T4, about 15 GB):** the full-precision 8B model (about 16 GB) does not fit, so
     use `--quant 4bit`. This is a declared deviation from the target paper. It is recorded in the
     run settings and output filename (`...-4bit`).
   - **L4 / A100 (Colab Pro):** use the default full precision (no `--quant`).
3. The question set and corpora contain CPIC text and are not on GitHub. Upload these files to
   your Google Drive folder `pgxtrust_data/`:
   `data/p02/items_v1.jsonl`, `data/p03/corpus_current.jsonl`, `data/p03/corpus_mixed.jsonl`,
   `data/p03/corpus_tagged.jsonl`.
4. Colab cells. The GitHub repo is private: either use a GitHub token in the clone URL, or upload
   a zip of `~/pgxtrust` (without `.venv` and `data/cpic_dumps`) and unzip it.
   ```python
   from google.colab import drive; drive.mount('/content/drive')
   # get the code into /content/pgxtrust (clone with a token, or unzip an upload), then:
   %cd /content/pgxtrust
   !pip install -q -e '.[colab]'
   !mkdir -p data/p02 data/p03
   !cp /content/drive/MyDrive/pgxtrust_data/items_v1.jsonl data/p02/
   !cp /content/drive/MyDrive/pgxtrust_data/corpus_*.jsonl data/p03/
   import os; os.environ["HF_TOKEN"] = "hf_..."   # paste your token; do not save the notebook with it
   ```
   ```python
   !python scripts/p03_run.py --arm A0 --backend llama --quant 4bit --limit 20 --tag smoke
   !for a in A0 A1 A2 A3; do python scripts/p03_run.py --arm $a --backend llama --quant 4bit; done
   !cp -r results/p03/runs /content/drive/MyDrive/pgxtrust_data/   # save results to Drive
   ```
   Re-run the same loop after a disconnect: finished questions are skipped.

## After the runs

Copy the result files back into `~/pgxtrust/results/p03/runs/` and tell Claude. The P04 analysis
(H1, H2, CIs, date-sensitivity, failure attribution) runs on those files only.
