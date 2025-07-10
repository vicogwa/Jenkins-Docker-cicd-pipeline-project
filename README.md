# Jenkins CI/CD Pipeline with Docker

A comprehensive containerized CI/CD pipeline implementation using Jenkins, Docker, and Python Flask for learning modern DevOps practices.

## 🎯 Project Overview

This project demonstrates a complete CI/CD pipeline setup that:
- Containerizes Jenkins with Docker-in-Docker capabilities
- Builds and tests a Python Flask application
- Deploys to a test environment automatically
- Implements pipeline-as-code with Jenkinsfile
- Follows DevOps best practices for automation and deployment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Source Code   │───▶│  Jenkins CI/CD  │───▶│ Test Environment│
│   (Git Repo)    │    │   (Container)   │    │   (Container)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Pipeline Flow:**
1. **Code Checkout** → Pull latest code from repository
2. **Build** → Create Docker image for the application
3. **Test** → Run unit tests in isolated container
4. **Security Scan** → Perform security checks (placeholder)
5. **Deploy** → Deploy to test environment
6. **Integration Tests** → Verify deployment with health checks

## 📁 Project Structure

```
jenkins-cicd-project/
├── 📄 docker-compose.yml          # Multi-container orchestration
├── 📄 Jenkinsfile                 # Pipeline definition (Infrastructure as Code)
├── 📄 README.md                   # This file
├── 📁 jenkins/                    # Jenkins configuration
│   ├── 📄 Dockerfile              # Custom Jenkins image with Docker
│   ├── 📄 plugins.txt             # Required Jenkins plugins
│   └── 📁 init.groovy.d/          # Startup configuration
│       └── 📄 basic-security.groovy
├── 📁 app/                        # Sample Python Flask application
│   ├── 📄 Dockerfile              # Application container definition
│   ├── 📄 requirements.txt        # Python dependencies
│   ├── 📁 src/                    # Source code
│   │   └── 📄 app.py              # Flask application
│   └── 📁 tests/                  # Test suite
│       └── 📄 test_app.py         # Unit tests
```

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:
- **Docker Desktop** (v20.10+)
- **Docker Compose** (v2.0+)
- **Git** (for version control)
- **Code Editor** (VS Code, IntelliJ, etc.)

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd jenkins-cicd-project
   ```

2. **Build and start the services:**
   ```bash
   docker-compose up -d
   ```

3. **Access Jenkins:**
   - Open: http://localhost:8080
   - Username: `admin`
   - Password: `admin123`

4. **Verify the application:**
   - Test environment: http://localhost:5000
   - Health check: http://localhost:5000/health

## 🔧 Configuration

### Jenkins Configuration

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

**Pre-installed Plugins:**
- Pipeline (workflow-aggregator)
- Docker Pipeline (docker-workflow)
- GitHub integration
- Email notifications
- Build utilities

### Application Configuration

**Environment Variables:**
- `APP_VERSION`: Application version (set during build)
- `ENV`: Environment type (development/test/production)
- `FLASK_ENV`: Flask environment setting

## 🔄 CI/CD Pipeline

### Pipeline Stages

| Stage | Description | Actions |
|-------|-------------|---------|
| **Checkout** | Retrieve source code | Pull latest code from Git |
| **Build** | Create Docker image | Build application container |
| **Test** | Run unit tests | Execute pytest in container |
| **Security Scan** | Security analysis | Placeholder for security tools |
| **Deploy** | Deploy to test env | Start container in test mode |
| **Integration Tests** | End-to-end testing | Health checks and API tests |

### Pipeline Features

- **Parallel Execution**: Tests can run in parallel
- **Automated Cleanup**: Failed builds trigger cleanup
- **Health Checks**: Deployment verification
- **Test Reporting**: JUnit test result publishing
- **Error Handling**: Graceful failure management

## 🛠️ Development Workflow

### Local Development

1. **Make code changes** in the `app/` directory
2. **Run tests locally:**
   ```bash
   cd app
   python -m pytest tests/ -v
   ```

3. **Test Docker build:**
   ```bash
   docker build -t test-app ./app
   docker run -p 5000:5000 test-app
   ```

4. **Commit and push changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin main
   ```

### Pipeline Execution

**Automatic Triggers:**
- Push to main branch
- Pull request creation
- Manual trigger via Jenkins UI

**Manual Pipeline Run:**
1. Login to Jenkins (http://localhost:8080)
2. Navigate to your pipeline job
3. Click "Build Now"
4. Monitor build progress in console output

## 📊 Monitoring & Logging

### View Build Logs
```bash
# Jenkins container logs
docker-compose logs jenkins

# Application logs
docker-compose logs test-app

# Follow logs in real-time
docker-compose logs -f
```

### Health Monitoring
```bash
# Check container status
docker-compose ps

# Test application health
curl http://localhost:5000/health
```

## 🔍 Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find what's using port 8080
netstat -ano | findstr :8080
# Kill the process
taskkill /PID <PID> /F
```

**Docker Build Fails:**
```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Jenkins Won't Start:**
```bash
# Check logs
docker-compose logs jenkins
# Restart Jenkins
docker-compose restart jenkins
```

### Debug Commands

```bash
# Access Jenkins container
docker exec -it jenkins-server bash

# Access application container
docker exec -it test-environment bash

# View detailed logs
docker-compose logs --timestamps
```

## 🚀 Advanced Features

### Multi-Environment Support

Add environment-specific configurations:
```yaml
# docker-compose.prod.yml
services:
  jenkins:
    environment:
      - ENV=production
      - APP_VERSION=${BUILD_NUMBER}
```

### Parallel Testing

Extend Jenkinsfile for parallel execution:
```groovy
stage('Parallel Tests') {
    parallel {
        stage('Unit Tests') {
            steps {
                sh 'python -m pytest tests/unit/ -v'
            }
        }
        stage('Integration Tests') {
            steps {
                sh 'python -m pytest tests/integration/ -v'
            }
        }
    }
}
```

### Notifications

Add Slack/Email notifications:
```groovy
post {
    failure {
        emailext(
            subject: "Build Failed: ${env.JOB_NAME}",
            body: "Build ${env.BUILD_NUMBER} failed. Check console output.",
            to: "team@company.com"
        )
    }
}
```

## 🔐 Security Considerations

### Best Practices Implemented

- **Container Isolation**: Each service runs in isolated containers
- **Non-root User**: Jenkins runs as non-root user
- **Secret Management**: Credentials stored in Jenkins credential store
- **Network Segmentation**: Services communicate through dedicated network

### Security Enhancements

1. **Enable HTTPS:**
   ```yaml
   environment:
     - JENKINS_OPTS="--httpPort=-1 --httpsPort=8443"
   ```

2. **Use external secrets:**
   ```yaml
   secrets:
     jenkins_admin_password:
       external: true
   ```

3. **Implement RBAC:**
   - Configure role-based access control
   - Use least privilege principle

## 🧪 Testing

### Test Types

**Unit Tests:**
- Test individual functions
- Mock external dependencies
- Fast execution

**Integration Tests:**
- Test API endpoints
- Database interactions
- Service communications

**End-to-End Tests:**
- Full application workflow
- Real environment testing
- User journey validation

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_app.py -v
```

## 📈 Performance Optimization

### Docker Optimization

**Multi-stage builds:**
```dockerfile
FROM python:3.9-slim as builder
RUN pip install --user -r requirements.txt

FROM python:3.9-slim
COPY --from=builder /root/.local /root/.local
```

**Layer caching:**
- Copy requirements before source code
- Use .dockerignore file
- Minimize layer count

### Jenkins Optimization

- **Parallel builds**: Enable concurrent builds
- **Build agents**: Use multiple build agents
- **Pipeline caching**: Cache dependencies between builds

## 🔄 Continuous Improvement

### Metrics to Monitor

- **Build Duration**: Track build time trends
- **Test Coverage**: Maintain >80% code coverage
- **Deployment Frequency**: Monitor deployment cadence
- **Failure Rate**: Track build success/failure rates

### Enhancement Opportunities

1. **Add code quality gates** (SonarQube)
2. **Implement blue-green deployments**
3. **Add performance testing** (JMeter)
4. **Integrate with monitoring** (Prometheus/Grafana)

## 📚 Learning Resources

### Key Concepts Covered

- **Infrastructure as Code**: Jenkinsfile, Docker Compose
- **Containerization**: Docker, multi-stage builds
- **CI/CD Pipelines**: Automated testing, deployment
- **DevOps Practices**: Monitoring, logging, security

### Next Steps

1. **Kubernetes Deployment**: Migrate to K8s
2. **GitOps**: Implement ArgoCD
3. **Service Mesh**: Add Istio for microservices
4. **Observability**: Implement comprehensive monitoring

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make changes and test**
4. **Submit pull request**

### Code Standards

- **Python**: Follow PEP 8 guidelines
- **Docker**: Use multi-stage builds
- **Jenkins**: Follow pipeline best practices
- **Git**: Use conventional commits

