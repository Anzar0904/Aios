# GitHub First Push Guide
## Step-by-Step Guide for Public Repository Deployment

Follow these commands to push the Personal AI OS codebase to GitHub for the first time and create the release tag.

---

## 1. Commit Local Release Artifacts

First, commit the updated `.gitignore`, release locks, and portfolio documents to the local repository:

```bash
# Add files (excluding ignored files)
git add .

# Verify what is staged (ensure no secrets or local databases are added)
git status

# Commit the release files
git commit -m "chore(release): finalize AI OS v1.0.0 release lock and portfolio assets"
```

---

## 2. Set Up the GitHub Remote

If not already done, create a repository on GitHub (e.g. `Aios` under user `Anzar0904`) and link it:

```bash
# Rename the default branch to main
git branch -M main

# Add the remote repository url
git remote add origin https://github.com/Anzar0904/Aios.git
```

---

## 3. Push to GitHub

Push the commit and local tags to the remote repository:

```bash
# Push the main branch
git push -u origin main

# Push the release tag
git push origin v1.0.0
```

---

## 4. Publish the GitHub Release

1. Navigate to your repository at: `https://github.com/Anzar0904/Aios/releases`
2. Click **Draft a new release**.
3. Choose the tag `v1.0.0`.
4. Set the Release Title to: `AI OS v1.0.0`
5. Copy the markdown content from **[`FINAL_GITHUB_RELEASE.md`](file:///Users/anzarakhtar/aios/FINAL_GITHUB_RELEASE.md)** and paste it into the description box.
6. Click **Publish release**.
