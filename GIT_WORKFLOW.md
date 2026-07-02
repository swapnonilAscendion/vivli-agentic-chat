# Git Workflow Guide - Pushing to Repository

## 🚀 Quick Start (First Time)

```bash
# 1. Initialize Git (if not already done)
cd c:\Users\swapnonil.mukherjee\projects\vivli-chatbot
git init

# 2. Add remote repository
git remote add origin https://github.com/your-username/vivli-chatbot.git

# 3. Create .env from template
cp .env.example .env
# Fill in your actual Azure credentials in .env

# 4. Verify .gitignore is in place
# .gitignore should already exist in the repo

# 5. Stage all files (except ignored ones)
git add .

# 6. Verify nothing sensitive is staged
git status
# Should NOT show .env, credentials, __pycache__, or .venv

# 7. Create initial commit
git commit -m "Initial commit: RAG chatbot with ingestion pipeline and rate limiting"

# 8. Push to GitHub
git push -u origin main
```

---

## 📋 Pre-Commit Checklist

**Before running `git add .`:**

- [ ] `.env` file exists and is filled with YOUR credentials
- [ ] `.gitignore` file exists in root directory
- [ ] `.env.example` exists as a template
- [ ] No credentials in any `.py` files
- [ ] No large files (> 100MB) to commit
- [ ] No build artifacts or cache directories

---

## 🔒 Safety Check (CRITICAL)

**Run this BEFORE committing:**

```bash
# Check what files are staged
git status

# Look for these - if you see them, STOP and remove:
❌ .env (should say "ignored" not "Changes to be committed")
❌ credentials.json
❌ *.key or *.pem files
❌ __pycache__/ directory
❌ venv/ directory

# If you see .env staged:
git reset .env
git status
# Now .env should show "ignored"

# Double-check with this command:
git diff --cached | grep -i "AZURE\|api\|key\|secret\|password"
# Should output NOTHING - if it does, you're about to leak credentials!
```

---

## 📁 Files to Commit (Summary)

### ALWAYS commit:
```
✓ **.py files
  - ingestion_pipeline.py
  - main.py
  - config.py
  - all source code

✓ **Documentation
  - README.md
  - *.md files
  - CLAUDE.md

✓ **.txt files
  - requirements.txt
  - .gitignore
  - .env.example (template only!)

✓ **Configuration (no secrets)
  - pytest.ini
  - setup.py
```

### NEVER commit:
```
❌ .env (real credentials)
❌ __pycache__/ (auto-generated)
❌ .venv/ or venv/ (virtual environment)
❌ *.pyc files (compiled Python)
❌ .vscode/, .idea/ (IDE settings)
❌ .DS_Store (macOS metadata)
❌ ingestion_checkpoint.json (runtime files)
```

---

## 🔄 Commit Workflow

### Step 1: Check Status
```bash
git status
```

**Good output:**
```
On branch main
nothing to commit, working tree clean
```

**Or:**
```
On branch main

Changes not staged for commit:
  modified: ingestion_pipeline.py
  modified: README.md

Untracked files:
  INGESTION_TIMING_GUIDE.md
```

**Bad output (STOP HERE!):**
```
Changes to be committed:
  new file: .env              ← WRONG! Remove this!
  modified: config.py
```

### Step 2: Stage Changes
```bash
# Stage all (but .gitignore will protect you)
git add .

# Or stage specific files
git add ingestion_pipeline.py README.md

# Verify what's staged
git status
# Should NOT show .env
```

### Step 3: Commit
```bash
# Write a clear commit message
git commit -m "Add rate limiting to ingestion pipeline

- Implement batch processing for embeddings
- Add configurable delays between batches
- Prevent 429 API rate limit errors
- Add timing estimation
- Update documentation"
```

**Good commit messages:**
- Clear and descriptive
- Explain WHAT and WHY, not just WHAT
- First line < 70 characters
- Separate subject from body with blank line

**Bad commit messages:**
```
❌ "fix bug"
❌ "update stuff"
❌ "asdf"
```

### Step 4: Push
```bash
# First time pushing to a branch
git push -u origin main

# Subsequent pushes
git push
```

---

## 🌳 Branch Workflow (Advanced)

If you want to use feature branches:

```bash
# Create a new branch for features
git checkout -b feature/add-resume-capability

# Make changes
git add .
git commit -m "Add checkpoint/resume functionality to ingestion"

# Push the branch
git push -u origin feature/add-resume-capability

# Create Pull Request on GitHub
# Once reviewed and approved:
git checkout main
git pull origin main
git merge feature/add-resume-capability
git push origin main

# Delete branch
git branch -d feature/add-resume-capability
git push origin --delete feature/add-resume-capability
```

---

## 📊 Common Git Commands

```bash
# See commit history
git log
git log --oneline        # Compact view
git log --graph --all    # Visual branch structure

# See what changed
git diff                 # Unstaged changes
git diff --cached        # Staged changes
git diff main origin/main # Compare with remote

# Undo changes
git restore filename.py  # Discard changes to file
git reset HEAD~1         # Undo last commit (keep changes)
git reset --hard HEAD~1  # Undo last commit (discard changes) ⚠️

# Pull latest from remote
git pull origin main

# Create new branch
git checkout -b new-branch-name

# Switch branch
git checkout main

# Delete branch
git branch -d branch-name
```

---

## 🚨 Oops! I Committed Something I Shouldn't Have

### If you committed .env locally (not pushed yet):

```bash
# Remove the file from the commit
git reset --soft HEAD~1
git reset .env
git add .
git commit -m "Remove accidentally committed .env"
```

### If you already pushed .env to GitHub:

```bash
# Remove from history (this is permanent!)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty -- --all

# Force push (warning: rewrites history!)
git push origin --force --all

# ⚠️ REGENERATE YOUR CREDENTIALS!
# Go to Azure Portal and rotate all keys immediately!
```

---

## 📝 Commit Message Convention

Follow this format:

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance

**Examples:**

```
feat: Add checkpoint/resume to ingestion pipeline

Implement checkpoint files to track ingestion progress.
If script fails halfway, can resume without re-embedding.

- Save progress after each batch
- Skip already-processed chunks on resume
- Prevent duplicate indexing

Closes #42
```

```
fix: Lower relevance threshold for keyword search

Keyword search scores are higher than vector search.
Threshold of 0.6 was filtering out valid results.
Lowered to 0.3 to match keyword search scoring.
```

---

## ✅ Pre-Push Verification

Before pushing to main:

```bash
# 1. Run tests (if you have them)
python -m pytest

# 2. Check code style
python -m pylint *.py

# 3. Verify no secrets
git diff HEAD origin/main | grep -i "key\|secret\|password"
# Should output nothing

# 4. Verify .env is not in commit
git log -p | grep "AZURE_OPENAI_API_KEY"
# Should output nothing

# 5. Check what will be pushed
git log --oneline origin/main..HEAD
# Review all commits

# 6. Final check
git status
# Should say "everything up to date" or only show unpushed commits

# 7. PUSH!
git push
```

---

## 🔗 GitHub Setup

### Create Repository on GitHub

```bash
# 1. Go to github.com
# 2. Click "New Repository"
# 3. Name: vivli-chatbot
# 4. Description: "RAG Chatbot for Vivli with intelligent document ingestion"
# 5. Visibility: Private (keep credentials safe!)
# 6. DO NOT initialize with README (we have one)
# 7. Create Repository
```

### Connect Local to GitHub

```bash
# Copy the HTTPS URL from GitHub
# Then:
git remote add origin https://github.com/your-username/vivli-chatbot.git
git branch -M main
git push -u origin main
```

---

## 🛡️ Keep Credentials Safe

**Golden Rules:**

1. ✅ Always use `.env.example` as a template
2. ✅ Always fill `.env` with YOUR credentials
3. ✅ Never commit `.env` to Git
4. ✅ Verify with `git status` before committing
5. ✅ Rotate keys if they leak
6. ✅ Make repository PRIVATE on GitHub
7. ✅ Use GitHub's Secret Scanning feature

---

## 📚 Additional Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## ✨ You're Ready!

```bash
# One final check
git status

# Should show:
# On branch main
# nothing to commit, working tree clean

# Or:
# On branch main
# Untracked files:
#   new-feature.md
# 
# nothing added to commit

# If you see .env - STOP and fix it first!

# Then push:
git push
```

**Your code is now safely backed up on GitHub! 🎉**
