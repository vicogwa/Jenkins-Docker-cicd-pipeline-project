pipeline {
    agent {
        docker {
            image 'docker:24.0-dind' // Docker-in-Docker image
            args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10')) // Retain only last 10 builds
    }

    parameters {
        string(name: 'DOCKER_REGISTRY', defaultValue: 'localhost:5000', description: 'Docker registry URL')
        string(name: 'APP_PORT', defaultValue: '5000', description: 'Port the app runs on')
        booleanParam(name: 'RUN_SECURITY_SCAN', defaultValue: true, description: 'Run security scan?')
        booleanParam(name: 'PUSH_TO_REGISTRY', defaultValue: false, description: 'Push image to registry?')
    }

    environment {
        APP_NAME = 'sample-app'
        IMAGE_TAG = "${params.DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}"
    }

    stages {
        stage('Verify Docker Setup') {
            steps {
                script {
                    echo '🔍 Verifying Docker setup...'
                    sh '''
                        # Start Docker daemon if using DinD
                        dockerd-entrypoint.sh &
                        sleep 10
                        
                        docker --version
                        docker info || echo "Docker info failed"
                        whoami && id && groups || echo "Group check failed"
                    '''
                }
            }
        }

        stage('Checkout Code') {
            steps {
                echo '📥 Checking out code...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "🐳 Building Docker image: ${IMAGE_TAG}"
                    sh """
                        docker build -t ${IMAGE_TAG} ./app
                    """
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    echo '🧪 Running unit tests in container...'
                    sh """
                        docker run --rm -v \$(pwd)/test-results:/app/test-results \
                        ${IMAGE_TAG} \
                        bash -c "cd /app && python -m pytest tests/ -v --junitxml=test-results/test-results.xml"
                    """
                }
            }
            post {
                always {
                    script {
                        if (fileExists('test-results/test-results.xml')) {
                            publishTestResults testResultsPattern: 'test-results/test-results.xml'
                        } else {
                            echo '⚠️ No test results found'
                        }
                    }
                }
            }
        }

        stage('Security Scan') {
            when {
                expression { params.RUN_SECURITY_SCAN }
            }
            steps {
                script {
                    echo '🔒 Running security scan (Trivy)...'
                    sh """
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy:latest image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_TAG} || true
                    """
                }
            }
        }

        stage('Deploy to Test Environment') {
            steps {
                script {
                    echo '🚀 Deploying to test environment...'
                    sh """
                        docker stop test-app || true
                        docker rm test-app || true

                        docker run -d --name test-app -p ${params.APP_PORT}:${params.APP_PORT} \
                        -e ENV=test -e APP_VERSION=${BUILD_NUMBER} \
                        ${IMAGE_TAG}
                    """
                    retry(5) {
                        sleep(time: 5, unit: 'SECONDS')
                        sh """
                            echo '🔍 Checking application health...'
                            curl -f http://localhost:${params.APP_PORT}/health
                        """
                    }
                    echo "✅ Application deployed successfully on port ${params.APP_PORT}!"
                }
            }
        }

        stage('Integration Tests') {
            steps {
                script {
                    echo '🔗 Running integration tests...'
                    sh """
                        for i in {1..5}; do
                            response=\$(curl -s http://localhost:${params.APP_PORT}/)
                            echo "Response: \$response"

                            if echo "\$response" | grep -q "Hello from CI/CD Pipeline!"; then
                                echo "✅ Integration test passed!"
                                exit 0
                            else
                                echo "❌ Integration test failed on attempt \$i, retrying..."
                                sleep 3
                            fi
                        done

                        echo "❌ Integration test failed after all attempts!"
                        exit 1
                    """
                }
            }
        }

        stage('Push to Docker Registry') {
            when {
                expression { params.PUSH_TO_REGISTRY }
            }
            steps {
                script {
                    echo "📤 Pushing image to registry: ${params.DOCKER_REGISTRY}"
                    sh """
                        docker tag ${IMAGE_TAG} ${params.DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                        docker push ${params.DOCKER_REGISTRY}/${APP_NAME}:${BUILD_NUMBER}
                    """
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Cleaning up...'
            script {
                node {
                    sh """
                        docker stop test-app || true
                        docker rm test-app || true
                        docker system prune -f || true
                    """
                }
            }
            cleanWs()
        }
        success {
            echo '✅ Pipeline succeeded!'
        }
        failure {
            echo '❌ Pipeline failed. Logs and containers cleaned up.'
        }
    }
}