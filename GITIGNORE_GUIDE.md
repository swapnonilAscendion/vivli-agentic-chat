# Git Ignore Guide - What's Being Excluded

## ⚠️ CRITICAL: Files NEVER to Commit

### Environment & Credentials
```
❌ .env                    ← Your Azure credentials!
❌ .env.local             ← Local overrides
❌ *.key, *.pem, *.crt    ← Encryption keys
❌ credentials.json       ← API keys
```

**Why:** These contain sensitive information that can be used to access your Azure account!

### Never commit:
```
AZURE_OPENAI_API_KEY="6TnS2NNUSUvaUfkN1sIRP52Q94Z..."
AZURE_SEARCH_ADMIN_KEY="yP2yPiwPR62cBZTg4Fr495kf..."
```

---

## 📦 Python Files (Auto-Generated)

```
❌ __pycache__/           ← Python cache
❌ *.pyc, *.pyo          ← Compiled Python
❌ .venv/, venv/         ← Virtual environment
❌ *.egg-info/           ← Package info
❌ dist/, build/         ← Build artifacts
```

**Why:** These are auto-generated and different on each machine

---

## 🔧 IDE & Editor Files

```
❌ .vscode/              ← VS Code settings
❌ .idea/                ← PyCharm settings
❌ *.swp, *.swo         ← Vim temporary files
❌ .DS_Store            ← macOS folder metadata
```

**Why:** These are personal and machine-specific

---

## 📊 Project-Specific (RAG Demo)

```
❌ ingestion_checkpoint.json   ← Runtime checkpoints
❌ resources/organized-data/   ← Large user data (optional)
❌ logs/                       ← Runtime logs
❌ *.db, *.sqlite             ← Local databases
```

**Why:** Too large, personally sensitive, or auto-generated

---

## ✅ What SHOULD be Committed

### Code Files
```
✓ *.py                 ← Python source code
✓ requirements.txt     ← Dependencies
✓ config.py           ← Configuration (no secrets)
```

### Documentation
```
✓ README.md           ← Project overview
✓ *.md files          ← Guides and documentation
✓ CLAUDE.md           ← Claude Code configuration
```

### Configuration (No Secrets)
```
✓ .gitignore          ← This file!
✓ pytest.ini          ← Test configuration
✓ setup.py            ← Package setup
```

### Example/Template Files
```
✓ .env.example        ← Template for credentials (DON'T FILL WITH REAL SECRETS!)
✓ config.example.py   ← Example configuration
```

---

## 🚀 Before Your First Commit

### 1. Create .env.example
```bash
# Create a template without actual secrets
cp .env .env.example

# Now edit .env.example and replace values with placeholders
# DO NOT commit the real .env!
```

**Example .env.example:**
```env
AZURE_OPENAI_API_KEY="your-key-here"
AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com/"
AZURE_SEARCH_ADMIN_KEY="your-search-key-here"
# ... etc
```

### 2. Verify Nothing Sensitive Gets Committed
```bash
# Check what files are staged
git status

# Make sure you don't see .env in the list!
# If you see it, unstage it:
git reset .env
```

### 3. Create .gitignore
✓ Already done! (This repository)

---

## 📋 Checklist Before Pushing

- [ ] **.env is NOT staged** - Should be ignored
- [ ] **credentials are NOT in any .py files** - Use .env only
- [ ] **API keys are NOT in config.py** - Should reference .env
- [ ] **__pycache__/ is ignored** - Auto-generated
- [ ] **.venv/ is ignored** - Virtual environment
- [ ] **Large data files are ignored** - Keep repo light
- [ ] **.env.example exists** - Template for others
- [ ] **.gitignore is committed** - Share ignore rules

---

## 🔍 Check for Accidents

### Before your first commit, run:

```bash
# Show what would be committed
git diff --cached

# Should NOT show any .env files or credentials!

# List all tracked files (check for secrets)
git ls-files

# Should NOT list .env, credentials, or sensitive files
```

### If you accidentally committed .env:

```bash
# Remove it from git history (BE CAREFUL!)
git rm --cached .env
git commit -m "Remove .env file (should have been ignored)"

# Then regenerate your credentials (they're now public!)
# Go to Azure Portal and rotate your API keys!
```

---

## 📝 .env.example Template

Create this file in the root directory:

```env
# ============================================================
# AZURE OPENAI
# ============================================================
AZURE_OPENAI_API_KEY="your-api-key-here"
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# ============================================================
# AZURE OPENAI DEPLOYMENTS
# ============================================================
AZURE_OPENAI_DEPLOYMENT_EMBEDDING=text-embedding-3-large
AZURE_OPENAI_DEPLOYMENT_LLM=gpt-4o-mini

# ============================================================
# AZURE AI SEARCH
# ============================================================
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_ADMIN_KEY="your-search-key-here"
AZURE_SEARCH_INDEX_NAME=vivli-knowledge-base

# ============================================================
# APPLICATION SETTINGS
# ============================================================
DEBUG=False
LOG_LEVEL=INFO
```

Then commit this template:
```bash
git add .env.example
git commit -m "Add .env.example template (no secrets)"
```

---

## 🛡️ Security Checklist

Before pushing:

1. **Scan for credentials**
   ```bash
   git diff --cached | grep -i "key\|secret\|password\|token"
   # Should return nothing!
   ```

2. **Check .env status**
   ```bash
   git status | grep .env
   # Should show: "ignored"
   ```

3. **Verify .gitignore**
   ```bash
   cat .gitignore | grep -E "^\.env|^credentials"
   # Should show these rules
   ```

4. **Final check before push**
   ```bash
   # See what will be pushed
   git log -p --not origin/main
   
   # Scan for anything that looks like a credential
   # Should see NONE!
   ```

---

## 🚨 If You Leak Credentials

If you accidentally push credentials to GitHub:

1. **IMMEDIATELY invalidate them**
   - Go to Azure Portal
   - Regenerate API keys
   - Delete old keys

2. **Remove from history**
   ```bash
   git filter-branch --force --index-filter \
     'git rm --cached --ignore-unmatch .env' \
     --prune-empty -- --all
   
   git push origin --force --all
   ```

3. **Alert your team** - Keys are compromised!

---

## 📚 Files in This Repository

### Root Directory
```
vivli-chatbot/
├── .env                           ❌ NOT committed (ignored)
├── .env.example                   ✓ Committed (template)
├── .gitignore                     ✓ Committed (this file)
└── rag-demo/
    ├── .env                       ❌ NOT committed (ignored)
    ├── requirements.txt           ✓ Committed
    ├── ingestion_pipeline.py      ✓ Committed
    ├── main.py                    ✓ Committed
    ├── config.py                  ✓ Committed (no secrets)
    ├── resources/organized-data/  ⚠️ Git-ignored (too large)
    └── __pycache__/              ❌ Auto-ignored
```

---

## ✨ GitHub Secret Scanning

GitHub automatically scans for leaked credentials:

- **GitHub Secret Scanning** will alert you if secrets are detected
- **Dependabot** will notify you of vulnerable dependencies
- **SAST** (Static Application Security Testing) scans for common issues

Even with .gitignore, use GitHub's protections!

---

## 🎯 Summary

**DO commit:**
- ✓ Python source code
- ✓ Documentation
- ✓ .env.example (template only)
- ✓ requirements.txt

**DON'T commit:**
- ❌ .env (real credentials)
- ❌ API keys or secrets
- ❌ Virtual environments
- ❌ Large data files
- ❌ IDE settings
- ❌ Auto-generated files

**Remember:** It's easier to prevent leaks than to fix them! 🛡️
