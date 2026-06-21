# GitHub Setup Instructions

## Quick Start

Follow these steps to push the `placemux-company-funnel` repo to GitHub:

### Step 1: Create the repo on GitHub
1. Go to [github.com/new](https://github.com/new)
2. Repository name: **placemux-company-funnel**
3. Description: "PlaceMux company-side funnel analysis dashboard (Phase 2 Task 3)"
4. Visibility: **Public**
5. Do NOT initialize with README, .gitignore, or license (we already have them)
6. Click **Create repository**

### Step 2: Add remote and push
Open a terminal in the project root and run:

```bash
cd placemux-company-funnel
git remote add origin https://github.com/maanvi3006-glitch/placemux-company-funnel.git
git branch -M main
git push -u origin main
```

### Step 3: Verify
- Go to `https://github.com/maanvi3006-glitch/placemux-company-funnel`
- You should see all your code, the screenshot, and commit history

## Troubleshooting

**"fatal: remote origin already exists"**
- Your repo already has a remote. Run: `git remote rm origin` first, then add the new one.

**Authentication error**
- If using HTTPS, you may need a GitHub Personal Access Token (PAT):
  1. Create a PAT at [github.com/settings/tokens](https://github.com/settings/tokens)
  2. Use it as your password when prompted
- Or use SSH: `git remote add origin git@github.com:maanvi3006-glitch/placemux-company-funnel.git`

