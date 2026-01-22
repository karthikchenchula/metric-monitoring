# GitHub Setup Guide

This guide will help you push the Metric Monitoring project to your GitHub repository.

## Prerequisites

- Git installed on your system
- GitHub account (https://github.com/karthikchenchula)
- Git configured with your credentials

## Step 1: Initialize Git Repository

Open terminal in the project directory and run:

```bash
git init
```

## Step 2: Configure Git (if not already done)

```bash
git config --global user.name "Karthik Chenchula"
git config --global user.email "your-email@example.com"
```

## Step 3: Add All Files

```bash
git add .
```

This will stage all files except those in `.gitignore`.

## Step 4: Create Initial Commit

```bash
git commit -m "Initial commit: Metric Monitoring for SAP BTP

- FastAPI application with 7 Prometheus metrics
- Content filtering with guardrails
- Token tracking for AI models
- GPU monitoring support
- SAP BTP integration ready
- Docker support
- Comprehensive documentation"
```

## Step 5: Create GitHub Repository

1. Go to https://github.com/karthikchenchula
2. Click the **+** icon (top right) → **New repository**
3. Repository name: `metric-monitoring`
4. Description: `AI Model Metrics Monitoring for SAP BTP with Prometheus integration`
5. Keep it **Public** (or Private if you prefer)
6. **DO NOT** initialize with README (we already have one)
7. Click **Create repository**

## Step 6: Add Remote Origin

Replace with your actual repository URL:

```bash
git remote add origin https://github.com/karthikchenchula/metric-monitoring.git
```

## Step 7: Push to GitHub

```bash
git branch -M main
git push -u origin main
```

## Step 8: Verify

Visit your repository at:
https://github.com/karthikchenchula/metric-monitoring

You should see:
- README.md displayed on the homepage
- All project files
- Documentation folder
- License file

## Alternative: Using Git GUI (VS Code)

If you prefer using VS Code:

1. Open VS Code in project folder
2. Click **Source Control** icon (left sidebar)
3. Click **Initialize Repository**
4. Stage all changes (click **+** next to Changes)
5. Enter commit message in text box
6. Click **✓ Commit**
7. Click **...** → **Remote** → **Add Remote**
8. Enter: `https://github.com/karthikchenchula/metric-monitoring.git`
9. Click **...** → **Push**

## Post-Push Steps

### 1. Add Topics/Tags

On GitHub repository page:
1. Click ⚙️ (settings icon) near "About"
2. Add topics: `python`, `fastapi`, `prometheus`, `sap-btp`, `metrics`, `monitoring`, `ai-models`

### 2. Enable GitHub Actions (Optional)

Create `.github/workflows/tests.yml` for automated testing:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirement.txt
      - name: Run tests
        run: python -m pytest Documentation/Test_Cases.py -v
```

### 3. Update Repository Settings

1. Go to repository **Settings**
2. Check **Wikis** if you want to add more docs
3. Add **Description** and **Website** URL (if deployed)

## Troubleshooting

### Authentication Issues

If you get authentication errors, you may need to use a Personal Access Token:

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Use token as password when pushing

Or use SSH:
```bash
git remote set-url origin git@github.com:karthikchenchula/metric-monitoring.git
```

### Large File Issues

If you encounter large file errors:
```bash
git rm --cached <large-file>
echo "<large-file>" >> .gitignore
git commit --amend
git push -f origin main
```

## Making Updates

After making changes:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

## Repository URL

Your repository will be available at:
**https://github.com/karthikchenchula/metric-monitoring**

## Clone Command for Others

Others can clone your repository using:
```bash
git clone https://github.com/karthikchenchula/metric-monitoring.git
```

---

**Note:** Make sure you review all files before pushing, especially if there are any sensitive credentials or API keys (none should be in this project, but good practice to check).
