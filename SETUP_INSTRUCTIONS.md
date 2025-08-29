# 🚀 Quick Setup Instructions for Gomaa Automation

## 📋 Prerequisites

- **Python 3.11+** installed on your system
- **uv** package manager installed (`pip install uv`)
- **Google Gemini API key** (get from [Google AI Studio](https://makersuite.google.com/app/apikey))
- **Laminar API key** (optional, get from [Laminar](https://laminar.ai))

## ⚡ Quick Start (Windows)

### Option 1: Automated Setup (Recommended)
1. **Double-click** `start_gomaa_automation.bat`
2. **Wait for installation** to complete
3. **Open your browser** to `http://localhost:5000`
4. **Configure your API keys** in the web interface:
   - Click on "Configuration" tab
   - Enter your Google Gemini API key
   - Enter your Laminar API key (optional)
   - Click "Save Configuration"
5. **Start testing** by clicking "Start Test"

### Option 2: Manual Setup
1. **Open Command Prompt** in this directory
2. **Run the following commands**:

```cmd
# Create virtual environment
uv venv --python 3.11

# Activate virtual environment
.venv\Scripts\activate.bat

# Install dependencies
uv sync

# Run the application
python professional_ai_automation.py
```

3. **Open your browser** to `http://localhost:5000`
4. **Configure API keys** through the web interface

## 🌐 Web Interface Configuration

### No .env File Required! 🎉

The application **does NOT require a .env file**. Instead, you configure everything through the web interface:

1. **API Keys**: Enter them directly in the Configuration tab
2. **Test Settings**: Modify website URL, focus areas, and testing options
3. **Real-time Updates**: All changes are saved automatically and applied immediately

### Configuration Options

- **Website URL**: The website you want to test
- **Test Focus**: Specific area to focus on (e.g., "about_us", "homepage", "contact")
- **Google API Key**: Your Gemini API key for AI-powered testing
- **Laminar API Key**: Optional Laminar integration for enhanced capabilities
- **Model**: AI model to use (default: gemini-2.5-flash)
- **Testing Options**: Choose which types of tests to run

## 🧪 Testing Your Setup

### 1. Basic Functionality Test
```cmd
python test_simple.py
```
This tests the core functionality without requiring external dependencies.

### 2. Web Interface Test
1. Start the application
2. Open `http://localhost:5000`
3. Verify the dashboard loads correctly
4. Check that configuration can be saved/loaded

### 3. API Key Test
1. Enter your Google API key in the configuration
2. Verify the key is saved correctly
3. Try starting a test to ensure the API works

## 🔧 Troubleshooting

### Common Issues

**"browser-use not available"**
```cmd
uv add browser-use
```

**"Laminar not available"**
```cmd
uv add lmnr
```

**"Flask not available"**
```cmd
uv add Flask Flask-SocketIO
```

**Port 5000 already in use**
- Change the port in the code or stop other services using port 5000

### API Key Issues

- **Invalid Google API Key**: Get a new key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Invalid Laminar API Key**: Get a new key from [Laminar](https://laminar.ai)
- **API Quota Exceeded**: Check your API usage limits

## 📁 File Structure

```
gomaa_automation/
├── professional_ai_automation.py  # Main application
├── templates/                     # HTML templates
│   └── professional_dashboard.html
├── requirements.txt               # Python dependencies
├── pyproject.toml                # Project configuration
├── README.md                     # Documentation
├── start_gomaa_automation.bat    # Windows startup script
├── test_simple.py                # Basic functionality test
└── SETUP_INSTRUCTIONS.md         # This file
```

## 🚀 Next Steps

1. **Install dependencies**: `uv sync`
2. **Run the app**: `python professional_ai_automation.py`
3. **Configure API keys** through the web interface
4. **Start testing** your websites!
5. **Customize** the testing parameters as needed

## 💡 Tips

- **Start Simple**: Begin with basic tests before enabling advanced features
- **Monitor Logs**: Check the console output for detailed execution information
- **Save Results**: Use the download feature to save test results for analysis
- **Batch Testing**: The app is designed for efficient batch testing, not individual element testing

## 🆘 Need Help?

- Check the console output for error messages
- Verify all dependencies are installed correctly
- Ensure your API keys are valid and have sufficient quota
- Test with the simple test script first: `python test_simple.py`

---

**🎯 Goal**: Get you up and running with professional AI-powered testing in minutes, not hours!
