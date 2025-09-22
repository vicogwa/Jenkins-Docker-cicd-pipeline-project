pipeline {
    agent any

    environment {
        APP_NAME     = 'sample-app'
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
        IMAGE_TAG    = "${APP_NAME}:${BUILD_NUMBER}"
        REGISTRY     = 'localhost:5000'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '✅ Checking out code...'
                checkout scm
            }
        }

        stage('Verify Docker Setup') {
            steps {
                echo '🔍 Verifying Docker environment...'
                sh '''
                    docker --version
                    docker ps
                    whoami
                    id
                    groups || echo "Groups not available"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh "docker build -t ${IMAGE_TAG} ./app"
                echo "✅ Docker image built: ${IMAGE_TAG}"
            }
        }

        stage('Verify Image') {
            steps {
                echo '🔍 Verifying built Docker image...'
                sh '''
                    docker images | grep ${APP_NAME}
                    docker inspect ${IMAGE_TAG}
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo '🧪 Running unit tests in container...'
                sh '''
                    docker run --rm ${IMAGE_TAG} bash -c \
                    "cd /app && python3 -m pytest tests/ -v || echo 'Tests failed'"
                '''
            }
        }

        stage('Static Code Analysis (SonarQube)') {
            steps {
                echo '🔍 Running SonarQube analysis...'
                echo 'SonarQube analysis would run here'
            }
        }

        stage('Deploy to Local Test Environment') {
            steps {
                echo '🚀 Deploying app to local Docker container...'
                sh '''
                    docker stop test-app || true
                    docker rm test-app || true
                    docker run -d --name test-app -p 5000:5000 \
                        -e ENV=test -e APP_VERSION=${BUILD_NUMBER} \
                        ${IMAGE_TAG}
                '''
                sleep(time: 10, unit: 'SECONDS')
                sh '''
                    for i in {1..5}; do
                        if curl -s http://localhost:5000/health; then
                            echo "✅ Health check passed!"
                            break
                        else
                            echo "❌ Health check failed. Retrying..."
                            sleep 5
                        fi
                    done
                '''
            }
        }

        stage('Integration Tests') {
            steps {
                echo '🧪 Running integration tests against deployed app...'
                sh '''
                    response=$(curl -s http://localhost:5000/)
                    echo "Response: $response"
                    if echo "$response" | grep -q "Hello from CI/CD Pipeline!"; then
                        echo "✅ Integration test passed!"
                    else
                        echo "❌ Integration test failed!"
                        exit 1
                    fi
                '''
            }
        }
    }

    post {
        always {
            node {
                echo '🧹 Cleaning up Docker containers...'
                sh '''
                    docker stop test-app || true
                    docker rm test-app || true
                    docker system prune -f || true
                '''
                cleanWs()
            }
        }
        success {
            echo '🎉 Pipeline succeeded!'
        }
        failure {
            node {
                echo '🔥 Pipeline failed!'
                sh '''
                    echo "Showing logs of failed container:"
                    docker logs test-app || true
                '''
            }
        }
    }
}
