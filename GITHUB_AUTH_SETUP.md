# 🔐 GitHub Authentication Setup for Claude Code

This guide will help you set up GitHub authentication so Claude Code can push commits to your repository.

## Current Setup Status ✅
- Repository: `https://github.com/wimbe3/ff-draft-app.git`
- Git Credential Helper: Windows Credential Manager (already configured)
- User configured: wimbe3

## 🔑 Option 1: GitHub Personal Access Token (Recommended)

This is the most secure and reliable method for Claude Code to push changes.

### Steps to Create a Personal Access Token:

1. **Go to GitHub Settings**
   - Visit: https://github.com/settings/tokens
   - Or: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**
   - Click "Generate new token" → "Generate new token (classic)"
   - Note: Give it a descriptive name like "Claude Code FF Draft App"
   
3. **Select Scopes**
   - ✅ `repo` (Full control of private repositories)
   - That's all you need!
   
4. **Generate and Copy Token**
   - Click "Generate token"
   - **IMPORTANT**: Copy the token immediately (you won't see it again!)
   - Token looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Store Token in Windows Credential Manager:

```bash
# Run this command in Claude Code after you have your token:
git config --global credential.helper manager
```

Then when you push, use this format:
```bash
# This will prompt for credentials once and save them
git push origin main
# Username: wimbe3
# Password: [paste your token here]
```

## 🔄 Option 2: GitHub CLI (gh) Authentication

Alternative method using GitHub's official CLI:

1. **Install GitHub CLI** (if not already installed)
   ```bash
   winget install --id GitHub.cli
   ```

2. **Authenticate with GitHub**
   ```bash
   gh auth login
   ```
   - Choose: GitHub.com
   - Choose: HTTPS
   - Choose: Login with web browser
   - Follow the prompts

3. **Configure Git to Use GitHub CLI**
   ```bash
   gh auth setup-git
   ```

## 🧪 Testing Authentication

Once set up, Claude Code can test with:

```bash
# Test pushing a small change
cd "C:\Users\CCunningham\Claude_Code\FF_Draft_App"
git add .
git commit -m "Test: Authentication setup"
git push origin main
```

## 🤖 For Claude Code to Push Changes

After authentication is set up, Claude Code can push changes using these commands:

```bash
# Standard workflow
git add .
git commit -m "Update: Description of changes"
git push origin main

# Or for specific files
git add specific_file.py
git commit -m "Fix: Specific issue"
git push
```

## 📝 Security Notes

### DO:
- Use Personal Access Tokens instead of passwords
- Set token expiration dates
- Use minimal required scopes
- Store tokens in credential manager

### DON'T:
- Share tokens in code or comments
- Commit tokens to repositories
- Use tokens in plain text files

## 🔧 Troubleshooting

### "Authentication Failed"
- Token may be expired - generate a new one
- Check token has `repo` scope
- Ensure using token as password, not actual GitHub password

### "Permission Denied"
- Verify you have write access to the repository
- Check token scopes include `repo`

### "Credential Manager Issues"
```bash
# Clear stored credentials
git config --global --unset credential.helper
git config --global credential.helper manager

# Or clear specific credentials
cmdkey /delete:git:https://github.com
```

## 🎯 Quick Setup Script

Run this in Claude Code to set everything up:

```bash
# Set user info
git config --global user.name "wimbe3"
git config --global user.email "your-email@example.com"

# Ensure credential helper is set
git config --global credential.helper manager

# Set default branch name
git config --global init.defaultBranch main

# Enable long paths (Windows specific)
git config --global core.longpaths true

echo "Git configuration complete! Now create a Personal Access Token on GitHub."
```

## ✅ Verification Checklist

- [ ] Personal Access Token created on GitHub
- [ ] Token has `repo` scope
- [ ] Token saved in password manager (for reference)
- [ ] Successfully pushed a test commit
- [ ] Claude Code can push updates

## 🚀 Ready to Use!

Once authenticated, you can ask Claude Code to:
- Push updates after making changes
- Create new branches
- Manage commits
- Update documentation

Just say: "Push these changes to GitHub" and Claude Code will handle it!

---

**Note**: Your token is stored securely in Windows Credential Manager and won't be visible in the repository or logs.