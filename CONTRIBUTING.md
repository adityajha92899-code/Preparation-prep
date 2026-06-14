## Contributing & Deploy

Steps to push this repo to GitHub and enable CI:

1. Create a GitHub repository and push this project:

```bash
git remote add origin https://github.com/<your-username>/<repo>.git
git branch -M main
git push -u origin main
```

2. In GitHub repository settings -> Secrets -> Actions, add the following secrets if you want live Google AI integration:
- `GOOGLE_AI_KEY`
- `PINECONE_API_KEY` (if used)

3. GitHub Actions will run `.github/workflows/ci.yml` on push/pull requests.

Optional: use the `gh` CLI to create repo programmatically:

```bash
gh repo create <your-username>/<repo> --public --source=. --push
```

CI uses Python 3.11 and runs `pytest` and uploads coverage XML.
