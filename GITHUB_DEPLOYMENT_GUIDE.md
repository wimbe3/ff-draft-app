# 📚 GitHub & Streamlit Community Cloud Deployment Guide

This guide will walk you through deploying your Fantasy Football Mock Draft Simulator to Streamlit Community Cloud via GitHub.

## 📋 Prerequisites

✅ **Completed**: Your app is ready with:
- Git repository initialized locally
- All files committed
- requirements.txt configured
- .gitignore and config files set up

❗ **Still Needed**:
- GitHub account (free at https://github.com)
- Streamlit Community Cloud account (free at https://streamlit.io/cloud)

## 🚀 Step 1: Create GitHub Repository

1. **Go to GitHub** and sign in (or create account)
   - Visit: https://github.com

2. **Create New Repository**
   - Click the "+" icon in top-right corner
   - Select "New repository"
   
3. **Configure Repository Settings**:
   ```
   Repository name: ff-draft-app
   Description: Fantasy Football Mock Draft Simulator with AI autopick
   Public: ✅ (Required for free Streamlit hosting)
   Initialize repository: ❌ (Don't check - we already have files)
   ```
   - Click "Create repository"

## 🔗 Step 2: Push Local Code to GitHub

After creating the repository, GitHub will show you commands. Use these in your terminal:

```bash
# Navigate to your project directory
cd "C:\Users\CCunningham\Claude_Code\FF_Draft_App"

# Add the GitHub repository as origin
git remote add origin https://github.com/YOUR_USERNAME/ff-draft-app.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

**Note**: Replace `YOUR_USERNAME` with your actual GitHub username.

### If you get authentication errors:

**Option A: Use Personal Access Token (Recommended)**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with "repo" scope
3. Use the token as your password when pushing

**Option B: Use GitHub Desktop**
1. Download GitHub Desktop: https://desktop.github.com/
2. Clone your repository
3. Copy your files to the cloned folder
4. Commit and push using the GUI

## ☁️ Step 3: Deploy to Streamlit Community Cloud

1. **Visit Streamlit Cloud**
   - Go to: https://streamlit.io/cloud
   - Click "Sign in" → "Continue with GitHub"
   - Authorize Streamlit to access your GitHub

2. **Deploy Your App**
   - Click "New app"
   - Fill in the deployment form:
     ```
     Repository: YOUR_USERNAME/ff-draft-app
     Branch: main
     Main file path: streamlit_app.py
     App URL: [choose-unique-name].streamlit.app
     ```
   - Click "Deploy"

3. **Wait for Deployment**
   - Streamlit will build your app (takes 2-5 minutes)
   - You'll see build logs in real-time
   - Once complete, your app will be live!

## 🔧 Step 4: Configuration & Secrets (Optional)

If you need to add secrets (API keys, passwords, etc.):

1. In Streamlit Cloud dashboard, click on your app
2. Click "Settings" → "Secrets"
3. Add secrets in TOML format:
   ```toml
   [database]
   username = "your_username"
   password = "your_password"
   ```

## 🔄 Step 5: Updates & Maintenance

### To Update Your App:

1. **Make changes locally**
   ```bash
   # Edit your files
   # Then commit and push
   git add .
   git commit -m "Update: description of changes"
   git push
   ```

2. **Automatic Deployment**
   - Streamlit automatically detects GitHub changes
   - Your app updates within minutes

### To Check App Status:
- Visit: https://share.streamlit.io
- View logs, usage stats, and manage settings

## 🎯 Your App URLs

Once deployed, you'll have:
- **Live App**: https://[your-app-name].streamlit.app
- **GitHub Repo**: https://github.com/YOUR_USERNAME/ff-draft-app

## 📱 Sharing Your App

Share your app by:
1. Sending the Streamlit URL directly
2. Adding the Streamlit badge to your README:
   ```markdown
   [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)
   ```
3. Embedding in an iframe on websites

## 🛠️ Troubleshooting

### Common Issues:

**Build Fails**
- Check requirements.txt for typos
- Ensure all imports are included
- Check Python version compatibility

**App Crashes**
- Check logs in Streamlit Cloud dashboard
- Verify file paths are relative, not absolute
- Ensure data files are included in repo

**Slow Performance**
- Optimize with st.cache_data decorators
- Reduce data file sizes
- Consider upgrading to paid tier for more resources

## 📊 Resource Limits (Free Tier)

- **Memory**: 1GB RAM
- **Storage**: 1GB
- **CPU**: Shared
- **Bandwidth**: Unlimited
- **Apps**: Unlimited public apps

## 🎉 Success Checklist

- [ ] GitHub account created
- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account created
- [ ] App deployed to Streamlit
- [ ] App URL tested and working
- [ ] README updated with live URL

## 📞 Getting Help

- **Streamlit Forum**: https://discuss.streamlit.io
- **GitHub Issues**: Create issue in your repo
- **Streamlit Docs**: https://docs.streamlit.io
- **Stack Overflow**: Tag with `streamlit`

## 🎈 Congratulations!

Your Fantasy Football Mock Draft Simulator is now live on the web! Share it with your league and enjoy drafting!

---

**Pro Tips**:
- Star your own repository to make it easier to find
- Add topics like "fantasy-football", "streamlit", "python" to your repo
- Create a demo video/GIF for your README
- Share on Reddit r/fantasyfootball for feedback