# 🍎 Installation Guide for macOS

## The Issue

On macOS, you need to use `pip3` instead of `pip`, and `python3` instead of `python`.

## Quick Fix

Run these commands:

```bash
# Step 1: Install dependencies (use minimal version for Python 3.9)
pip3 install -r requirements-minimal.txt

# OR if that doesn't work:
python3 -m pip install --user -r requirements-minimal.txt

# Step 2: Set up environment
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here

# Step 3: Run server
python3 run_server.py
```

## What's the Difference?

- `pip` → Use `pip3` on macOS
- `python` → Use `python3` on macOS
- `requirements.txt` → Use `requirements-minimal.txt` for Python 3.9

## Complete Step-by-Step

### 1. Check Your Python Version
```bash
python3 --version
```

If it shows Python 3.9.x, use `requirements-minimal.txt`
If it shows Python 3.10+, you can use `requirements.txt`

### 2. Install Dependencies

**For Python 3.9:**
```bash
pip3 install -r requirements-minimal.txt
```

**For Python 3.10+:**
```bash
pip3 install -r requirements.txt
```

**If you get permission errors:**
```bash
pip3 install --user -r requirements-minimal.txt
```

### 3. Create .env File
```bash
cp .env.example .env
```

Edit `.env` and add:
```
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the Server
```bash
python3 run_server.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### 5. Test It
Open a new terminal and test:
```bash
curl http://localhost:8001/health
```

Should return: `{"status":"ok","service":"wandersure"}`

## Troubleshooting

### "pip3: command not found"
```bash
# Install pip
python3 -m ensurepip --upgrade

# Or install Python via Homebrew
brew install python3
```

### "Permission denied"
```bash
# Use --user flag
pip3 install --user -r requirements-minimal.txt
```

### "Module not found" after installation
```bash
# Make sure you're using python3
python3 run_server.py
```

### "GROQ_API_KEY not set"
```bash
# Edit .env file
nano .env
# Add: GROQ_API_KEY=your_key_here
```

## Using Virtual Environment (Recommended)

For better isolation:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Now pip works without pip3
pip install -r requirements-minimal.txt

# Run server
python run_server.py

# When done, deactivate
deactivate
```

## Summary

**Just run:**
```bash
pip3 install -r requirements-minimal.txt
cp .env.example .env
# Edit .env to add GROQ_API_KEY
python3 run_server.py
```

That's it! 🎉

