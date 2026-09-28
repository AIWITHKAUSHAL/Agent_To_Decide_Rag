# Submission status and publishing

Prepared locally: application source, fictional policy, automated tests, 24-question offline routing CSV/JSON, teaching guide, and YouTube recording script.

Not yet completed: authenticated live model evaluation, a published GitHub repository, and a recorded/uploaded YouTube video. No public URLs are fabricated.

## 1. Run the live evaluation

Configure your local `.env`, then run:

```powershell
python evaluation.py --live
```

Inspect `results/live.json` and `results/live.csv`. Confirm the mode is `live` and review errors, routes, retrieved evidence, formulas, and answers. The files are ignored by default to avoid accidentally publishing query contents; only include them after review. Do not claim the offline baseline's score as LLM performance.

## 2. Publish to your GitHub repository

Create an empty repository in your own GitHub account, then run these commands from this folder, replacing YOUR_ACCOUNT with your account name:

```powershell
git init
git add .
git commit -m "Build student selective RAG agent with routing evaluation"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/selective-rag-agent.git
git push -u origin main
```

To include reviewed live results, explicitly stage the two result files with `git add -f results/live.json results/live.csv`, then commit and push. Never force-add `.env` or query logs.

## 3. Record and publish the explanation

Use `docs/YOUTUBE_SCRIPT.md` as your narration and screen-recording guide. Show the real running app and actual test results. Upload the recording to your own YouTube channel as public or unlisted according to the assignment. Include the GitHub link in the description.

## Submit these three actual links

- GitHub repository URL.
- Routing CSV URL inside the repository, clearly labelled live or offline.
- YouTube watch URL for the recorded explanation.
