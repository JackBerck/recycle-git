# Batch Resource Deleter (GitHub & Vercel)

> A fast, zero-dependency Python CLI tool to batch delete GitHub repositories and Vercel projects effortlessly.

[![CI](https://github.com/JackBerck/recycle-git/actions/workflows/ci.yml/badge.svg)](https://github.com/JackBerck/recycle-git/actions)
[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

## 🌟 Features

- ⚡ **Zero External Dependencies** — Built entirely with Python standard library (`urllib`). No `pip install` required.
- 🐙 **GitHub Batch Repo Deleter** — Scans public & private GitHub repositories and deletes selected items.
- 📐 **Vercel Batch Project Deleter** — Scans Vercel projects (personal & team accounts) and batch deletes selected projects.
- 🎯 **Flexible Selection** — Select items by index numbers (`1, 3, 5`), ranges (`2-5`), name keywords (`my-app`), or `all`.
- 🔄 **Interactive CLI Menu** — Access GitHub or Vercel tools via a simple interactive menu (`main.py`).
- 🛡️ **Safety Confirmation** — Explicit confirmation prompt (`DELETE`) prevents accidental deletions.

---

## 📋 Prerequisites

Before running the tool, ensure you have:

1. **Python 3.6 or higher** installed on your system (`python --version`).
2. A **GitHub Personal Access Token (PAT Classic)** (for GitHub repos) and/or a **Vercel Access Token** (for Vercel projects).

---

## 🔑 Token Setup

### 🐙 GitHub Personal Access Token (PAT)
1. Go to **GitHub Settings** ➔ **Developer Settings** ➔ **Personal Access Tokens** ➔ **Tokens (classic)**.
2. Select required scopes:
   - ✅ `delete_repo` *(Required to delete repositories)*
   - ✅ `repo` *(Required to scan private repositories)*

### 📐 Vercel Access Token
1. Go to **Vercel Dashboard** ➔ **Account Settings** ➔ **Tokens**.
2. Click **Create Token** and copy the generated token.
3. *(Optional)* If managing team projects, copy your **Team ID** from Vercel Team Settings.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/JackBerck/recycle-git.git
cd recycle-git
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and configure your tokens:
```env
GITHUB_TOKEN=ghp_your_github_token_here
VERCEL_TOKEN=your_vercel_access_token_here
# VERCEL_TEAM_ID=team_xxxxxxxx  (Optional: for team projects)
```

*(Alternatively, if `.env` is omitted, the scripts will prompt for tokens at runtime).*

### 3. Run the CLI Launcher
```bash
python main.py
```
Or run individual scripts directly:
```bash
python delete_repos.py           # GitHub Repositories
python delete_vercel_projects.py # Vercel Projects
```

---

## 💡 Usage & Selection Syntax

When prompted, you can select items using flexible input formats:

- **Single or Multiple Indices:** `1` or `1, 3, 5` or `1 3 5`
- **Index Range:** `2-5`
- **Project/Repo Name / Substring:** `my-app`
- **All Items:** `all` or `*`

After entering your selection, type `DELETE` when prompted to execute permanent deletion.

---

## ⚠️ Security Notice

> [!CAUTION]
> Resource deletion via REST API is **PERMANENT and CANNOT BE UNDONE**. Always review selected items before typing `DELETE`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
