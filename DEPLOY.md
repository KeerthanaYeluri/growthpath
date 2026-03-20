# Deploy GrowthPath to PythonAnywhere (Free Forever)

## Step 1: Create GitHub Repo
1. Go to https://github.com/new
2. Create repo named `growthpath` (public or private)
3. Don't initialize with README

## Step 2: Push Code to GitHub
Run these commands in the project folder:
```bash
cd interview
git add .
git commit -m "GrowthPath - Adaptive Learning Platform"
git remote add origin https://github.com/YOUR_USERNAME/growthpath.git
git branch -M main
git push -u origin main
```

## Step 3: Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com
2. Sign up for FREE account (Beginner)
3. Your app will be at: `yourusername.pythonanywhere.com`

## Step 4: Set Up on PythonAnywhere

### 4a. Open Bash Console
- Go to **Consoles** tab → **Bash** → Start a new console

### 4b. Clone Your Repo
```bash
git clone https://github.com/YOUR_USERNAME/growthpath.git
```

### 4c. Install Dependencies
```bash
cd growthpath/backend
pip3 install --user -r requirements.txt
```

### 4d. Create Data Directory
```bash
mkdir -p data/recordings
```

## Step 5: Configure Web App

### 5a. Go to **Web** tab → **Add a new web app**
1. Click "Add a new web app"
2. Select **Manual configuration**
3. Select **Python 3.10** (or latest available)

### 5b. Set WSGI Configuration
Click on the **WSGI configuration file** link and replace ALL contents with:
```python
import sys
import os

project_home = '/home/YOUR_USERNAME/growthpath/backend'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['JWT_SECRET'] = 'your-secret-key-change-this-to-something-random'

from app import app as application
```

### 5c. Set Virtual Environment (optional)
If you created a virtualenv, set the path. Otherwise skip.

### 5d. Set Static Files
In the **Static files** section, add:
- URL: `/static/` → Directory: `/home/YOUR_USERNAME/growthpath/frontend/`

### 5e. Set Source Code
- Source code: `/home/YOUR_USERNAME/growthpath/backend`
- Working directory: `/home/YOUR_USERNAME/growthpath/backend`

## Step 6: Reload & Test
1. Click **Reload** button on the Web tab
2. Visit `https://yourusername.pythonanywhere.com`
3. Register, login, start learning!

## Updating the App
When you push new code to GitHub:
```bash
# On PythonAnywhere Bash console:
cd ~/growthpath
git pull
# Then click "Reload" on the Web tab
```

## Free Tier Limits
- 512MB storage (enough for thousands of users)
- 1 web app
- CPU seconds limited but generous for this app
- Always on - no sleeping/cold starts
- Custom domain NOT available on free tier
