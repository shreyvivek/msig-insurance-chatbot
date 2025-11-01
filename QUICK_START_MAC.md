# 🚀 Quick Start Guide for macOS

## Step 1: Install Dependencies

On macOS, use `pip3` instead of `pip`:

**If you have Python 3.9 (recommended for compatibility):**
```bash
pip3 install -r requirements-minimal.txt
```

**If you have Python 3.10+:**
```bash
pip3 install -r requirements.txt
```

**Alternative: Use python3 -m pip**
```bash
python3 -m pip install --user -r requirements-minimal.txt
```

**Alternative methods if pip3 doesn't work:**

```bash
# Method 1: Use python3 -m pip
python3 -m pip install -r requirements.txt

# Method 2: If you get permission errors, use --user flag
pip3 install --user -r requirements.txt

# Method 3: Use Homebrew to install Python (recommended)
brew install python3
pip3 install -r requirements.txt
```

## Step 2: Set Up Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit it with your favorite editor
nano .env
# or
open -e .env
# or
code .env  # if you have VS Code
```

Add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

## Step 3: Run Server

Use `python3` instead of `python`:

```bash
python3 run_server.py
```

## Step 4: Run Frontend (Optional)

```bash
cd frontend
npm install
npm run dev
```

## Troubleshooting

### Issue: "pip3: command not found"
**Solution**: Install Python via Homebrew:
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3
```

### Issue: "Permission denied" when installing
**Solution**: Use `--user` flag:
```bash
pip3 install --user -r requirements.txt
```

### Issue: "python3: command not found"
**Solution**: Check if Python is installed:
```bash
which python3
# If nothing, install Python (see above)
```

### Issue: "Module not found" errors
**Solution**: Make sure you're using the right Python:
```bash
# Check which Python you're using
which python3

# Install packages to that Python
python3 -m pip install -r requirements.txt
```

## Recommended: Use a Virtual Environment

For better isolation, use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Now pip will work
pip install -r requirements.txt

# Run server
python run_server.py

# When done, deactivate
deactivate
```

## Quick Commands Summary

```bash
# Install dependencies
pip3 install -r requirements.txt

# OR with virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add GROQ_API_KEY

# Run server
python3 run_server.py

# Run frontend (new terminal)
cd frontend
npm install
npm run dev
```

