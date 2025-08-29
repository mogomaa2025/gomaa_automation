#!/usr/bin/env python3
"""
Professional AI Automation - Enterprise-Grade Software Testing Suite
A Flask application that provides a professional testing interface with:
- Comprehensive bug type checklists
- Efficient batch testing (not individual element testing)
- Professional test case structures (test steps, test data, expected results)
- Senior tester-like behavior and reporting
- Integration with Gemini API and Laminar for enhanced capabilities
"""

import os
import sys
import json
import re
import threading
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from enum import Enum

# Fix Unicode encoding issues on Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, render_template, jsonify, request, redirect, url_for, send_file
from flask_socketio import SocketIO, emit
import tempfile

# Import Laminar and Gemini dependencies
try:
    from lmnr import Laminar
    from browser_use import Agent, ChatGoogle, ChatOpenAI, ChatGroq, ChatOllama
    from browser_use.browser import BrowserSession
    LAMINAR_AVAILABLE = True
    print("✅ Laminar and browser-use available")
except ImportError as e:
    LAMINAR_AVAILABLE = False
    print(f"⚠️  Laminar or browser-use not available: {e}")
    print("   Install with: uv add browser-use lmnr")

# Initialize Laminar if available (will be done when API key is provided)
LAMINAR_INITIALIZED = False

def initialize_laminar_if_needed():
    """Initialize Laminar if API key is provided and not already initialized"""
    global LAMINAR_INITIALIZED
    
    if (LAMINAR_AVAILABLE and 
        test_config["laminar_api_key"] and 
        test_config["laminar_api_key"] != "your_laminar_key_here" and
        not LAMINAR_INITIALIZED):
        try:
            Laminar.initialize()
            LAMINAR_INITIALIZED = True
            print("✅ Laminar initialized successfully")
            return True
        except Exception as e:
            print(f"⚠️  Laminar initialization failed: {e}")
            return False
    return LAMINAR_INITIALIZED

app = Flask(__name__)
app.config['SECRET_KEY'] = 'professional-ai-automation-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
test_status = {
    "is_running": False,
    "is_paused": False,
    "current_test_case": 0,
    "total_test_cases": 0,
    "progress_percentage": 0,
    "current_url": "",
    "status_message": "Ready for professional testing",
    "current_focus_area": "",
    "test_coverage": {}
}

# Professional test configuration with dual API support
test_config = {
    "website_url": "https://demoblaze.com/",
    "provider": "google",
    "google_api_key": "",  # For backward compatibility with old configs
    "openai_api_key": "",
    "groq_api_key": "",
    "laminar_api_key": "",
    "model": "gemini-1.5-flash",
    "headless": False,
    "custom_prompt": "",
    "window_width": 1920,
    "window_height": 1080,
    "api_keys_configured": False
}

# Professional test results storage
test_results = {
    "test_cases": [],
    "bug_reports": [],
    "test_suites": [],
    "coverage_reports": [],
    "execution_logs": [],
    "recommendations": []
}

# Global testing framework
test_execution_thread = None
stop_event = threading.Event()

def datetime_to_string(obj):
    """Convert datetime objects to ISO format strings for JSON serialization"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def prepare_data_for_socket(data):
    """Prepare data for Socket.IO by converting datetime objects and enums"""
    if isinstance(data, dict):
        return {k: prepare_data_for_socket(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [prepare_data_for_socket(item) for item in data]
    elif isinstance(data, Enum):
        return data.value
    else:
        return datetime_to_string(data)

def save_config_to_file():
    """Save current configuration to file"""
    try:
        config_to_save = test_config.copy()
        with open("professional_test_config.json", "w") as f:
            json.dump(config_to_save, f, indent=2)
        print("Professional configuration saved to file")
    except Exception as e:
        print(f"Error saving configuration: {e}")

def save_results_to_file():
    """Save current results to file"""
    try:
        results_to_save = {
            "test_status": test_status.copy(),
            "test_results": test_results.copy(),
            "test_config": test_config.copy(),
            "saved_time": datetime.now().isoformat()
        }
        
        with open("professional_test_results.json", "w") as f:
            json.dump(results_to_save, f, indent=2)
        print("Professional test results saved to file")
    except Exception as e:
        print(f"Error saving results: {e}")

def create_llm(provider: str, model: str, api_key: str = None):
    """Factory function to create an LLM instance based on the provider."""
    if not LAMINAR_AVAILABLE:
        raise ValueError("browser-use is not installed. Cannot create LLM.")

    if provider == "google":
        if not api_key:
            raise ValueError("Google API key is required for Gemini models.")
        return ChatGoogle(model=model, api_key=api_key)
    elif provider == "openai":
        if not api_key:
            raise ValueError("OpenAI API key is required for OpenAI models.")
        return ChatOpenAI(model=model, api_key=api_key)
    elif provider == "groq":
        if not api_key:
            raise ValueError("Groq API key is required for Groq models.")
        return ChatGroq(model=model, api_key=api_key)
    elif provider == "ollama":
        # Ollama doesn't typically require an API key
        return ChatOllama(model=model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

class ProfessionalTestController:
    """Controls professional test execution with senior tester behavior"""
    
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.execution_log = []
        
    def log(self, message, level="INFO"):
        """Log message and emit to web interface"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "datetime": datetime.now().isoformat()
        }
        self.execution_log.append(log_entry)
        print(f"[{timestamp}] {level}: {message}")
        socketio.emit('log_message', log_entry)

    def _create_browser_session(self):
        """Creates and returns a browser session based on test configuration."""
        self.log("🖥️  Creating browser session...", "INFO")
        return BrowserSession(
            headless=test_config["headless"],
            window_size={"width": test_config["window_width"], "height": test_config["window_height"]},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

    def _generate_test_task(self):
        """Generates the task prompt for the AI agent based on user instructions."""

        instructions = test_config.get("custom_prompt", "Perform a general test of the website.")

        prompt = f"""
        You are a senior QA tester. Your goal is to test the website: {test_config['website_url']}.

        Please follow these instructions:
        {instructions}

        Your task is to identify bugs, usability issues, or any unexpected behavior.

        Here are some rules to follow:
        -   Do not get stuck in a loop. If you perform an action, try a different action next.
        -   Your test should not exceed 8 steps.
        -   Provide a summary of your findings at the end.
        """
        return prompt

    def _parse_final_report(self, report_text: str):
        """Parses the agent's final markdown report to extract test cases and bugs."""

        bug_reports = []

        # A more robust regex to find bug reports
        bug_pattern = re.compile(
            r"## Bug Report\n\n\*\*Bug Summary:\*\* (.*?)\n\n\*\*Description:\*\* (.*?)\n\n\*\*Steps to Reproduce:\*\*\n(.*?)\n\n\*\*Expected Result:\*\* (.*?)\n\n\*\*Actual Result:\*\* (.*?)\n",
            re.DOTALL
        )

        matches = bug_pattern.finditer(report_text)

        for match in matches:
            steps_to_reproduce_raw = match.group(3).strip()
            steps = [step.strip().lstrip('0123456789. ') for step in steps_to_reproduce_raw.split('\n')]

            bug_reports.append({
                "bug_id": f"BUG_{len(bug_reports) + 1}",
                "title": match.group(1).strip(),
                "description": match.group(2).strip(),
                "steps_to_reproduce": steps,
                "expected_behavior": match.group(4).strip(),
                "actual_behavior": match.group(5).strip(),
                "severity": "Medium",  # Default severity
                "category": "Functional",
                "reported_date": datetime.now().isoformat(),
                "status": "OPEN"
            })

        return {"bug_reports": bug_reports}

    def _create_planner_prompt(self, website_url: str):
        """Creates the prompt for the planner agent."""
        return f"""
        You are a senior QA engineer responsible for creating a test plan for the website: {website_url}.

        Your task is to explore the website and generate a comprehensive list of test cases.

        The output must be a JSON object containing a single key "test_cases".
        The value of "test_cases" must be an array of strings.
        Each string in the array should be a concise, descriptive name for a single test case.

        Example:
        {{
          "test_cases": [
            "Test user login with valid credentials.",
            "Test user login with invalid credentials.",
            "Test adding an item to the shopping cart.",
            "Test navigating to the 'About Us' page and verifying its content."
          ]
        }}

        Please provide only the JSON object as your response. Do not include any other text or explanations.
        """

    async def generate_test_plan(self, website_url: str):
        """Runs the planner agent to generate a test plan."""
        self.log(f"🤖 Starting test plan generation for {website_url}...", "INFO")

        try:
            provider = test_config["provider"]
            model = test_config["model"]
            api_key = test_config.get(f"{provider}_api_key")

            llm = create_llm(provider=provider, model=model, api_key=api_key)
            task = self._create_planner_prompt(website_url)

            agent = Agent(task=task, llm=llm, max_steps=1) # Only one step: generate the plan
            
            history = await agent.run()

            final_report_text = ""
            if history:
                # The history object is iterable
                final_step = next((s for s in reversed(list(history)) if s.is_done), None)
                if final_step:
                    final_report_text = final_step.long_term_memory or ""

            self.log(f"Received test plan from agent: {final_report_text}", "INFO")

            try:
                json_match = re.search(r"```json\n(.*)\n```", final_report_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    plan = json.loads(json_str)
                else:
                    plan = json.loads(final_report_text)

                socketio.emit('test_plan_generated', plan)
            except json.JSONDecodeError:
                self.log("Failed to parse JSON from planner agent output.", "ERROR")
                socketio.emit('test_plan_generated', {"error": "Failed to generate test plan."})

        except Exception as e:
            self.log(f"Error during test plan generation: {e}", "ERROR")
            socketio.emit('test_plan_generated', {"error": str(e)})

    def _create_executor_prompt(self, test_case: str):
        """Creates the prompt for the executor agent."""
        return f"""
        You are a meticulous QA test executor. Your sole task is to execute a single test case precisely as described and report the outcome.

        **Website:** {test_config['website_url']}
        **Test Case to Execute:** {test_case}

        **Instructions:**
        1.  Follow the steps outlined in the test case.
        2.  After execution, determine if the test case passed or failed.
        3.  If it failed, provide a detailed bug report in markdown format.
        4.  Conclude your response with a single word: `PASS` or `FAIL`.
        """

    async def run_test_cases(self, test_cases: list):
        """Runs a list of test cases, one by one."""
        self.log(f"🤖 Starting execution of {len(test_cases)} test cases...", "INFO")

        for i, test_case in enumerate(test_cases):
            self.log(f"Running Test Case {i+1}/{len(test_cases)}: {test_case}", "INFO")
            socketio.emit('test_case_update', {"test_case": test_case, "status": "RUNNING"})

            try:
                provider = test_config["provider"]
                model = test_config["model"]
                api_key = test_config.get(f"{provider}_api_key")

                llm = create_llm(provider=provider, model=model, api_key=api_key)
                task = self._create_executor_prompt(test_case)
                agent = Agent(task=task, llm=llm, max_steps=8)

                history = await agent.run()

                final_report_text = ""
                if history:
                    final_step = next((s for s in reversed(list(history)) if s.is_done), None)
                    if final_step:
                        final_report_text = final_step.long_term_memory or ""

                parsed_results = self._parse_final_report(final_report_text)
                bugs = parsed_results.get("bug_reports", [])
                status = "FAIL" if bugs else "PASS"

                socketio.emit('test_case_update', {
                    "test_case": test_case,
                    "status": status,
                    "bugs": bugs
                })

            except Exception as e:
                self.log(f"Error running test case '{test_case}': {e}", "ERROR")
                socketio.emit('test_case_update', {
                    "test_case": test_case,
                    "status": "ERROR",
                    "error": str(e)
                })

        self.log("✅ Test execution completed.", "SUCCESS")

    # The old test suite logic is now deprecated in favor of the two-phase workflow.

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main professional testing dashboard"""
    return render_template('professional_dashboard.html')

@app.route('/api/status')
def get_status():
    """Get current test status"""
    return jsonify(test_status)

@app.route('/api/results')
def get_results():
    """Get professional test results"""
    return jsonify(test_results)

@app.route('/api/config')
def get_config():
    """Get current configuration"""
    return jsonify(test_config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update test configuration"""
    global test_config
    
    try:
        data = request.json
        if data:
            # First, update the provider if it's in the data
            if 'provider' in data:
                test_config['provider'] = data['provider']

            # Now, update the rest of the config
            for key, value in data.items():
                if key == "api_key" and value:
                    provider = test_config['provider']
                    if provider == 'google':
                        test_config['google_api_key'] = value
                    elif provider == 'openai':
                        test_config['openai_api_key'] = value
                    elif provider == 'groq':
                        test_config['groq_api_key'] = value
                elif key in test_config:
                    test_config[key] = value

            # Check if any relevant API key is configured
            google_key = test_config.get("google_api_key", "")
            openai_key = test_config.get("openai_api_key", "")
            groq_key = test_config.get("groq_api_key", "")
            
            if (google_key or openai_key or groq_key):
                test_config["api_keys_configured"] = True
                # Try to initialize Laminar if needed
                initialize_laminar_if_needed()
            else:
                test_config["api_keys_configured"] = False
        
        # Save configuration to file
        save_config_to_file()
        
        return jsonify({"status": "updated", "config": test_config})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_sample_data')
def load_sample_data():
    """Load sample professional test data for demonstration"""
    global test_results
    
    # Create sample professional test cases
    test_results.update({
        "test_cases": [
            {
                "test_id": "BATCH_ABOUT_US_CONTENT_ELEMENTS",
                "title": "Batch Test: Content Elements on About Us",
                "description": "Efficiently test all content elements together on the about us page",
                "priority": "P1",
                "status": "PASSED",
                "execution_time": 2.5,
                "test_steps": [
                    {"step_number": 1, "action": "Test headings and text functionality and appearance", "expected_result": "headings and text should work correctly and look good", "status": "PASSED"},
                    {"step_number": 2, "action": "Test images and media functionality and appearance", "expected_result": "images and media should work correctly and look good", "status": "PASSED"}
                ],
                "created_date": datetime.now().isoformat(),
                "tester": "AI Testing Agent"
            },
            {
                "test_id": "BATCH_ABOUT_US_LAYOUT_ELEMENTS",
                "title": "Batch Test: Layout Elements on About Us",
                "description": "Efficiently test all layout elements together on the about us page",
                "priority": "P1",
                "status": "FAILED",
                "execution_time": 3.2,
                "test_steps": [
                    {"step_number": 1, "action": "Test header section functionality and appearance", "expected_result": "header section should work correctly and look good", "status": "PASSED"},
                    {"step_number": 2, "action": "Test main content area functionality and appearance", "expected_result": "main content area should work correctly and look good", "status": "FAILED"}
                ],
                "created_date": datetime.now().isoformat(),
                "tester": "AI Testing Agent"
            }
        ],
        "bug_reports": [
            {
                "bug_id": "BUG_20241201_143022_1",
                "title": "Test failure in Batch Test: Layout Elements on About Us",
                "description": "Step 2: Test main content area functionality and appearance",
                "severity": "MEDIUM",
                "category": "UI Layout",
                "steps_to_reproduce": ["Navigate to the test page", "Execute test case: Batch Test: Layout Elements on About Us", "Reach step 2: Test main content area functionality and appearance"],
                "expected_behavior": "main content area should work correctly and look good",
                "actual_behavior": "Element test failed",
                "environment": "AI Testing Environment",
                "browser": "Chrome (via browser-use)",
                "device": "Desktop",
                "screen_resolution": "1920x1080",
                "tester": "AI Testing Agent",
                "reported_date": datetime.now().isoformat(),
                "status": "OPEN"
            }
        ],
        "coverage_reports": [
            {
                "timestamp": datetime.now().isoformat(),
                "coverage": {
                    "Functional Testing": 85.0,
                    "UI/UX Testing": 90.0,
                    "Responsiveness Testing": 75.0,
                    "Accessibility Testing": 60.0,
                    "Performance Testing": 80.0,
                    "Security Testing": 70.0,
                    "Browser Compatibility": 85.0,
                    "Content Testing": 95.0
                }
            }
        ],
        "recommendations": [
            "Increase test coverage for Accessibility Testing (currently 60.0%)",
            "Increase test coverage for Security Testing (currently 70.0%)",
            "Focus on fixing 1 high-severity bugs first"
        ]
    })
    
    # Save sample data to file
    save_results_to_file()
    
    # Emit results update
    results_data = prepare_data_for_socket(test_results)
    socketio.emit('results_update', results_data)
    
    return jsonify({"status": "sample_data_loaded"})

@app.route('/api/save_results')
def save_results():
    """Save current results to file"""
    try:
        save_results_to_file()
        return jsonify({"status": "saved", "filename": "professional_test_results.json"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_results')
def load_results():
    """Load results from file"""
    global test_results, test_status, test_config
    
    try:
        if os.path.exists("professional_test_results.json"):
            with open("professional_test_results.json", "r") as f:
                data = json.load(f)
                
            if "test_results" in data:
                test_results = data["test_results"]
            if "test_status" in data:
                test_status.update(data["test_status"])
            if "test_config" in data:
                test_config.update(data["test_config"])
            
            # Emit updates
            results_data = prepare_data_for_socket(test_results)
            status_data = prepare_data_for_socket(test_status)
            
            socketio.emit('results_update', results_data)
            socketio.emit('status_update', status_data)
            
            return jsonify({"status": "loaded"})
        else:
            return jsonify({"error": "No results file found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear_results')
def clear_results():
    """Clear all test results"""
    global test_results, test_status
    
    test_results.update({
        "test_cases": [],
        "bug_reports": [],
        "test_suites": [],
        "coverage_reports": [],
        "execution_logs": [],
        "recommendations": []
    })
    
    test_status.update({
        "is_running": False,
        "is_paused": False,
        "current_test_case": 0,
        "total_test_cases": 0,
        "progress_percentage": 0,
        "current_url": "",
        "status_message": "Ready for professional testing",
        "current_focus_area": "",
        "test_coverage": {}
    })
    
    # Save cleared state
    save_results_to_file()
    
    # Emit updates
    results_data = prepare_data_for_socket(test_results)
    status_data = prepare_data_for_socket(test_status)
    
    socketio.emit('results_update', results_data)
    socketio.emit('status_update', status_data)
    
    return jsonify({"status": "cleared"})

@app.route('/api/run_tests', methods=['POST'])
def run_tests_route():
    """Kicks off the test execution in a background thread."""
    try:
        data = request.json
        test_cases = data.get('test_cases')
        if not test_cases:
            return jsonify({"error": "No test cases provided."}), 400

        def run_execution_in_background():
            controller = ProfessionalTestController()
            asyncio.run(controller.run_test_cases(test_cases))

        thread = threading.Thread(target=run_execution_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "execution_started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_test_plan', methods=['POST'])
def generate_test_plan_route():
    """Kicks off the test plan generation in a background thread."""
    try:
        data = request.json
        website_url = data.get('website_url')
        if not website_url:
            return jsonify({"error": "Website URL is required."}), 400

        # Update config from the request
        test_config['website_url'] = website_url
        test_config['provider'] = data.get('provider', 'google')
        test_config['model'] = data.get('model', 'gemini-1.5-flash')

        provider = test_config['provider']
        api_key = data.get('api_key')
        if api_key:
            test_config[f"{provider}_api_key"] = api_key

        save_config_to_file()

        def run_generation_in_background():
            controller = ProfessionalTestController()
            asyncio.run(controller.generate_test_plan(website_url))

        thread = threading.Thread(target=run_generation_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({"status": "generating_plan"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/results/download')
def download_results():
    """Download test results as JSON"""
    # Create temporary file with results
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "test_status": test_status,
            "test_results": test_results,
            "test_config": test_config,
            "download_time": datetime.now().isoformat()
        }, f, indent=2)
        temp_path = f.name
    
    return send_file(temp_path, as_attachment=True, download_name=f"professional_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

# ============================================================================
# SOCKET.IO EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected")
    emit('connected', {"status": "connected"})
    
    # Send current status and results
    status_data = prepare_data_for_socket(test_status)
    results_data = prepare_data_for_socket(test_results)
    
    emit('status_update', status_data)
    emit('results_update', results_data)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_saved_config():
    """Load saved configuration on startup"""
    global test_config
    
    try:
        if os.path.exists("professional_test_config.json"):
            with open("professional_test_config.json", "r") as f:
                saved_config = json.load(f)
                test_config.update(saved_config)
                print("Professional configuration loaded from file")
    except Exception as e:
        print(f"Error loading configuration: {e}")

def load_saved_results():
    """Load saved results on startup"""
    global test_results, test_status
    
    try:
        if os.path.exists("professional_test_results.json"):
            with open("professional_test_results.json", "r") as f:
                data = json.load(f)
                
            if "test_results" in data:
                test_results = data["test_results"]
            if "test_status" in data:
                test_status.update(data["test_status"])
            if "test_config" in data:
                test_config.update(data["test_config"])
                
            print("Professional test results loaded from file")
    except Exception as e:
        print(f"Error loading results: {e}")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == '__main__':
    # Load saved configuration and results
    load_saved_config()
    load_saved_results()
    
    # Run the Flask app
    print("🚀 Starting Professional AI Automation Flask server...")
    print("Web interface will be available at:")
    print("  - Local: http://localhost:5000")
    print("  - Network: http://0.0.0.0:5000")
    print("Press Ctrl+C to stop the server")
    
    if not LAMINAR_AVAILABLE:
        print("⚠️  WARNING: browser-use not available.")
        print("   Install required dependencies: uv add browser-use lmnr")
        print("   The app will work but can't execute tests.")
    else:
        print("✅ browser-use available - AI automation enabled!")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
