import docker
from prometheus_api_client import PrometheusConnect
import logging
from pythonjsonlogger import jsonlogger
from flask import Flask, render_template
import threading
import time
import subprocess
import json
from dotenv import load_dotenv
import os
import requests  # For DeepSeek API calls

# Configure logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

load_dotenv()

class MCPServer:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.prom = PrometheusConnect(url="http://prometheus:9090")
        self.incidents = []
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"  # Update with actual API URL
        
    def monitor_applications(self):
        while True:
            self.check_containers()
            self.check_metrics()
            time.sleep(30)
    
    def check_containers(self):
        try:
            for container in self.docker_client.containers.list():
                if container.status != 'running':
                    self.handle_incident(
                        f"Container {container.name} is down",
                        container.name,
                        context={
                            "container_id": container.id,
                            "container_name": container.name,
                            "image": container.image.tags,
                            "logs": container.logs().decode('utf-8')[-1000:]  # Last 1KB of logs
                        }
                    )
        except Exception as e:
            logger.error("Container check failed", exc_info=True)
    
    def check_metrics(self):
        try:
            # Check app1 error rate
            error_rate = self.prom.get_current_metric_value(
                'rate(flask_http_request_total{status="500"}[1m])'
            )
            if error_rate and float(error_rate[0]['value'][1]) > 0:
                self.handle_incident(
                    "High error rate in App1",
                    "app1",
                    severity="high",
                    context={
                        "metric": "flask_http_request_total",
                        "value": float(error_rate[0]['value'][1])
                    }
                )
        except Exception as e:
            logger.error("Metrics check failed", exc_info=True)
    
    def handle_incident(self, message, app, severity="medium", context=None):
        incident = {
            "timestamp": time.time(),
            "message": message,
            "application": app,
            "severity": severity,
            "status": "open",
            "context": context or {}
        }
        self.incidents.append(incident)
        logger.warning("Incident detected", extra=incident)
        
        # Trigger auto-remediation
        self.attempt_auto_remediation(incident)
    
    def attempt_auto_remediation(self, incident):
        if not self.deepseek_api_key:
            logger.warning("DeepSeek API key not configured - skipping auto-remediation")
            return
            
        # Step 1: Analyze the issue with DeepSeek LLM
        analysis = self.analyze_with_deepseek(incident)
        if not analysis:
            return
            
        # Step 2: Get remediation steps
        remediation = self.get_remediation_steps(incident, analysis)
        
        # Step 3: Execute remediation if confident
        if remediation.get('confidence', 0) > 0.7:  # 70% confidence threshold
            self.execute_remediation(remediation['steps'], incident)
        else:
            logger.info(f"Low confidence remediation - requires manual review: {remediation}")
    
    def analyze_with_deepseek(self, incident):
        prompt = f"""
        Analyze this system incident and identify the likely root cause:
        
        Application: {incident['application']}
        Message: {incident['message']}
        Severity: {incident['severity']}
        Context: {json.dumps(incident['context'], indent=2)}
        
        Provide a concise technical analysis of the problem.
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",  # Update with correct model name
                "messages": [
                    {"role": "system", "content": "You are a DevOps engineer analyzing system incidents."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3  # Lower temperature for more deterministic responses
            }
            
            response = requests.post(self.deepseek_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error("DeepSeek analysis failed", exc_info=True)
            return None
    
    def get_remediation_steps(self, incident, analysis):
        prompt = f"""
        Based on this incident analysis, provide remediation steps:
        
        Incident: {json.dumps(incident, indent=2)}
        Analysis: {analysis}
        
        Respond in JSON format with:
        - "root_cause": brief description
        - "steps": array of commands/actions
        - "confidence": 0-1 rating of solution confidence
        - "risks": potential risks of these steps
        
        Only respond with valid JSON.
        """
        
        try:
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a DevOps engineer providing remediation steps."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(self.deepseek_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error("Failed to get remediation steps", exc_info=True)
            return {"error": str(e)}
    
    def execute_remediation(self, steps, incident):
        logger.info(f"Executing remediation steps for {incident['application']}")
        
        for step in steps:
            try:
                # For container-related actions
                if step['action'] == 'restart_container':
                    container = self.docker_client.containers.get(step['container'])
                    container.restart()
                    logger.info(f"Restarted container: {step['container']}")
                
                # For shell commands
                elif step['action'] == 'run_command':
                    result = subprocess.run(
                        step['command'],
                        shell=True,
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    logger.info(f"Command executed: {step['command']}")
                
                # Add more action types as needed
                
            except Exception as e:
                logger.error(f"Remediation step failed: {step}", exc_info=True)
                incident['status'] = 'remediation_failed'
                return
        
        incident['status'] = 'resolved'
        logger.info(f"Incident resolved: {incident['message']}")
    
    def start_web_ui(self):
        app = Flask(__name__)
        
        @app.route('/')
        def dashboard():
            status = {
                "applications": [
                    {"name": "app1", "status": self.get_app_status("app1")},
                    {"name": "app2", "status": self.get_app_status("app2")}
                ],
                "incidents": self.incidents[-5:][::-1],
                "llm_enabled": bool(self.deepseek_api_key)
            }
            return render_template('dashboard.html', **status)
        
        app.run(host='0.0.0.0', port=8000)
    
    def get_app_status(self, app_name):
        try:
            container = self.docker_client.containers.get(app_name)
            return "running" if container.status == "running" else "down"
        except:
            return "unknown"

if __name__ == '__main__':
    mcp = MCPServer()
    
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=mcp.monitor_applications)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Start web UI
    mcp.start_web_ui()