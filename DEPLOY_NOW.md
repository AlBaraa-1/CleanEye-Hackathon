# 🚀 DEPLOYMENT STEPS - Follow This Exactly

## ⏰ Total Time: ~1 hour

---

# PART 1: HUGGING FACE SPACES (30-45 min)

## Step 1: Create Space on Hugging Face (5 min)

1. **Open browser and go to:**
   ```
   https://huggingface.co/spaces
   ```

2. **Make sure you're logged in as: AlBaraa63**

3. **Click "Create new Space"** (top right)

4. **Fill in the form:**
   ```
   Owner: AlBaraa63
   Space name: cleaneye-garbage-detection
   License: MIT
   Select SDK: Streamlit
   Space hardware: CPU basic (free)
   Visibility: Public
   ```

5. **Click "Create Space"**

✅ **Your Space URL:** https://huggingface.co/spaces/AlBaraa63/cleaneye-garbage-detection

---

## Step 2: Prepare Files on Your Computer (15 min)

### A. Create deployment folder

```powershell
cd C:\Users\POTATO\Desktop\codeing\Computer-vision\CleanEye
mkdir HF_Deploy
cd HF_Deploy
```

### B. Copy the cloud-optimized app

```powershell
copy ..\app_cloud.py .\app.py
```

### C. Copy requirements

```powershell
copy ..\requirements_cloud.txt .\requirements.txt
```

### D. Copy model weights

```powershell
mkdir Weights
copy ..\Weights\best.pt .\Weights\best.pt
```

### E. Create README.md

Create a new file `README.md` with this content:

```markdown
---
title: CleanEye - AI Garbage Detection
emoji: 🗑️
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.38.0
app_file: app.py
pinned: false
license: mit
tags:
  - computer-vision
  - yolov8
  - garbage-detection
  - mcp
  - sustainability
---

# 🗑️ CleanEye - AI Garbage Detection Agent

**MCP-enabled AI agent for real-time garbage detection and smart city monitoring**

Built for **MCP 1st Birthday Hackathon** - Track 2: MCP in Action (Agents)

## 🎯 Features

- 🤖 **YOLOv8 Detection** - Trained on 4000+ images
- 📊 **6 Waste Categories** - Comprehensive classification  
- 🎯 **Severity Analysis** - Clean, Moderate, Severe levels
- 🔌 **MCP Integration** - Agent-callable tools for LLMs

## 🚀 How to Use

1. Upload an image containing garbage/waste
2. Adjust confidence threshold if needed
3. Click "Detect Garbage"
4. View results with bounding boxes and statistics

## 📊 Performance

- **Accuracy**: 85%+ mAP
- **Training Data**: 4000+ annotated images
- **Categories**: 6 types of waste
- **Speed**: <1 second per image

## 🏆 Hackathon Project

**Track**: MCP in Action (Agents)  
**Developer**: AlBaraa AlOlabi (@AlBaraa63)  
**Period**: November 14-30, 2025

## 🔗 Links

- **GitHub**: https://github.com/AlBaraa-1/Computer-vision/tree/main/CleanEye
- **MCP Server**: Full agent implementation with 4 MCP tools

## 📄 License

MIT License

---

*Making cities cleaner with AI agents* 🌍
```

✅ **You should now have in HF_Deploy folder:**
- app.py
- requirements.txt
- Weights/best.pt
- README.md

---

## Step 3: Upload to Hugging Face (15 min)

### Option A: Web Upload (EASIER - Recommended)

1. **Go to your Space:**
   ```
   https://huggingface.co/spaces/AlBaraa63/cleaneye-garbage-detection
   ```

2. **Click "Files" tab**

3. **Upload files one by one:**
   - Click "Add file" → "Upload files"
   - Upload `README.md`
   - Upload `requirements.txt`
   - Upload `app.py`
   
4. **Upload model weights:**
   - Click "Add file" → "Create a new file"
   - Name it: `Weights/best.pt`
   - This creates the Weights folder
   - Delete that file
   - Now upload your actual `best.pt` into Weights folder

5. **Wait for build** (5-10 minutes)
   - Click "Logs" tab to watch progress
   - Wait for "Running on" message

### Option B: Git Upload (Advanced)

```powershell
# Install Git LFS
git lfs install

# Clone your Space
git clone https://huggingface.co/spaces/AlBaraa63/cleaneye-garbage-detection
cd cleaneye-garbage-detection

# Copy all files from HF_Deploy
copy ..\HF_Deploy\* . /Y
copy ..\HF_Deploy\Weights\* .\Weights\ /Y

# Track large files with LFS
git lfs track "*.pt"
git add .gitattributes

# Commit and push
git add .
git commit -m "Deploy CleanEye for MCP Hackathon"
git push
```

---

## Step 4: Test Your HF Space (5 min)

1. **Wait for deployment to finish**
   - Check "Logs" tab
   - Look for "Running on" message

2. **Test the app:**
   - Go to "App" tab
   - It should load automatically
   - Upload a test image
   - Verify detection works

3. **Save your URL:**
   ```
   https://huggingface.co/spaces/AlBaraa63/cleaneye-garbage-detection
   ```

✅ **HF Spaces deployment COMPLETE!**

---

# PART 2: STREAMLIT CLOUD (15-20 min)

## Step 1: Sign Up (5 min)

1. **Go to:**
   ```
   https://streamlit.io/cloud
   ```

2. **Click "Sign in with GitHub"**

3. **Authorize with your GitHub account: AlBaraa-1**

4. **Free tier is automatic**

✅ **Streamlit Cloud account ready!**

---

## Step 2: Make Sure Code is on GitHub (10 min)

### Update your GitHub repository:

```powershell
cd C:\Users\POTATO\Desktop\codeing\Computer-vision

# Add all new files
git add .

# Commit
git commit -m "Add MCP integration and cloud deployment files"

# Push to GitHub
git push origin main
```

✅ **Verify on GitHub:**
- Go to: https://github.com/AlBaraa-1/Computer-vision
- Check that CleanEye folder has all files
- Especially: app_cloud.py, requirements_cloud.txt

---

## Step 3: Deploy to Streamlit Cloud (5 min)

1. **Go back to Streamlit Cloud dashboard**

2. **Click "New app"**

3. **Fill in deployment settings:**
   ```
   Repository: AlBaraa-1/Computer-vision
   Branch: main
   Main file path: CleanEye/app_cloud.py
   App URL: cleaneye-garbage-detection (or auto-generate)
   ```

4. **Advanced settings (click to expand):**
   ```
   Python version: 3.12
   Requirements file: CleanEye/requirements_cloud.txt
   ```

5. **Click "Deploy!"**

6. **Wait for build** (5-10 minutes)
   - Streamlit will install dependencies
   - Build and start your app
   - You'll see progress in real-time

---

## Step 4: Get Your Streamlit URL (1 min)

Your app will be live at something like:
```
https://cleaneye-garbage-detection.streamlit.app
```

Streamlit will show you the exact URL.

✅ **Streamlit Cloud deployment COMPLETE!**

---

# 🎉 FINAL CHECKLIST

## Hugging Face Spaces:
- [ ] Space created at HF
- [ ] Files uploaded (README, requirements, app.py, model)
- [ ] Build completed successfully
- [ ] App tested and working
- [ ] URL saved: https://huggingface.co/spaces/AlBaraa63/cleaneye-garbage-detection

## Streamlit Cloud:
- [ ] Signed up with GitHub
- [ ] Code pushed to GitHub
- [ ] App deployed from repository
- [ ] Build completed successfully
- [ ] App tested and working
- [ ] URL saved: https://[your-app].streamlit.app

## GitHub:
- [ ] All code pushed
- [ ] Repository is public
- [ ] URL: https://github.com/AlBaraa-1/Computer-vision

---

# 📝 YOUR THREE SUBMISSION URLS

Copy these for your hackathon submission:

**Primary Demo (Hugging Face):**
```
https://huggingface.co/spaces/AlBaraa63/cleaneye-garbage-detection
```

**Backup Demo (Streamlit):**
```
https://[your-app].streamlit.app
```

**Source Code (GitHub):**
```
https://github.com/AlBaraa-1/Computer-vision/tree/main/CleanEye
```

---

# 🐛 TROUBLESHOOTING

## HF Space won't build?

**Check logs tab for errors:**

- **"No module named 'cv2'"** → Make sure requirements.txt has opencv-python-headless
- **"Model file not found"** → Verify Weights/best.pt was uploaded
- **"Out of memory"** → Model is large, try upgrading Space hardware (may cost)

**Common fixes:**
```powershell
# Re-create requirements.txt without version pins
streamlit
ultralytics
opencv-python-headless
numpy
pillow
torch
torchvision
pandas
pyyaml
```

## Streamlit Cloud errors?

**File path issues:**
- Make sure app_cloud.py is in CleanEye folder
- Verify requirements_cloud.txt path is correct
- Check that Weights/best.pt exists in repo

**Build fails:**
- Check Python version is 3.12
- Verify all imports in app_cloud.py
- Make sure model file is committed to Git (use Git LFS if needed)

## Both apps slow?

**Normal for free tiers!**
- Large model + limited resources = slower
- HF Spaces can upgrade hardware (paid)
- Streamlit Cloud has resource limits
- Still works, just be patient

---

# ✅ YOU'RE DONE!

Once both deployments are complete, you have:

✅ Two live demo URLs
✅ Source code on GitHub  
✅ Ready for hackathon submission
✅ Professional presentation

**Time to celebrate! 🎉**

Next steps:
1. Test both URLs thoroughly
2. Take screenshots for documentation
3. Start planning your demo video
4. Join Discord to share your project

---

**Need help? Check DUAL_DEPLOYMENT.md for more details!**
