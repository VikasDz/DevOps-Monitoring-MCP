# Auto-Remediation Monitoring & Control Platform 

## 🚀 Features
- Real-time container monitoring
- AI-powered incident diagnosis
- Automated remediation workflows
- Isolated logging pipelines

## 📦 Prerequisites
```bash
# Required Tools
- Docker Desktop 4.15+
- Python 3.9+
- Node.js 14.x (for App2)
```

## 🛠️ Installation
```bash
# Clone the repository
git clone https://github.com/VikasDz/DevOps-Monitoring-MCP.git
cd DevOps-Monitoring-MCP

# Set up environment
cp .env.example .env
nano .env  # Add your DeepSeek API key

# Build and launch
docker-compose up -d --build
```

## 🌐 Service Endpoints
| Service      | URL                   | Credentials       |
|--------------|-----------------------|-------------------|
| Grafana      | http://localhost:3000 | admin:grafana     |
| Prometheus   | http://localhost:9090 | -                 |
| Kibana       | http://localhost:5601 | -                 |
| MCP Dashboard| http://localhost:8000 | -                 |

## 🐳 Docker Commands Cheatsheet
```bash
# View running containers
docker-compose ps

# Check MCP logs
docker-compose logs -f mcp

# Force rebuild
docker-compose up -d --force-recreate

# Full cleanup
docker-compose down -v && docker system prune -a
```

## 📝 Sample prometheus.yml
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'app1'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['app1:5000']
  
  - job_name: 'app2'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['app2:3000']
```

## 🤖 Testing Auto-Remediation
```python
# Trigger test failure (50% error rate)
import requests
for _ in range(5):
    requests.get('http://localhost:5000/error')
    
# Verify remediation
docker-compose logs mcp | grep "Attempting remediation"
```

## 🗂️ Project Structure
```
ARM-CP/
├── apps/
│   ├── app1/               # Flask app
│   │   ├── app.py
│   │   └── requirements.txt
│   └── app2/               # Node.js app
│       ├── app.js
│       └── package.json
├── monitoring/
│   ├── prometheus.yml
│   ├── grafana/
│   └── logstash/
│       ├── app1.conf
│       └── app2.conf
├── mcp-server/
│   ├── app.py              # Control plane
│   └── requirements.txt
└── docker-compose.yml
```

## 💡 How the AI Integration Works
```python

def analyze_incident(self, error_log):
    prompt = f"""
    Analyze this Docker container error:
    {error_log}
    
    Suggest remediation steps in JSON format with:
    - root_cause
    - steps[]
    - confidence_score
    """
    
    response = requests.post(
        self.deepseek_url,
        headers={"Authorization": f"Bearer {self.api_key}"},
        json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
    )
    return response.json()
```

## 🆘 Support
For issues, please:
1. Check container logs
```bash
docker-compose logs --tail=100
```
2. Open a GitHub Issue
3. Include your `docker-compose version` output

