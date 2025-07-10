pipeline {
    agent any
    
    environment {
        APP_NAME = 'sample-app'
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
        IMAGE_TAG = "${APP_NAME}:${BUILD_NUMBER}"
        REGISTRY = 'localhost:5000' // Local registry for demo
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    def image = docker.build("${IMAGE_TAG}", "./app")
                    echo "Built image: ${IMAGE_TAG}"
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo 'Running tests in container...'
                    docker.image("${IMAGE_TAG}").inside {
                        sh '''
                            cd /app
                            python -m pytest tests/ -v --junitxml=test-results.xml
                        '''
                    }
                }
            }
            post {
                always {
                    // Archive test results
                    publishTestResults testResultsPattern: 'test-results.xml'
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    echo 'Running security scan...'
                    // Example with Trivy (you can install it in Jenkins container)
                    sh '''
                        echo "Security scan placeholder"
                        echo "In production, you would run tools like:"
                        echo "trivy image ${IMAGE_TAG}"
                    '''
                }
            }
        }
        
        stage('Deploy to Test Environment') {
            steps {
                script {
                    echo 'Deploying to test environment...'
                    
                    // Stop existing container if running
                    sh '''
                        docker stop test-app || true
                        docker rm test-app || true
                    '''
                    
                    // Run new container
                    docker.image("${IMAGE_TAG}").run(
                        "--name test-app -p 5000:5000 -e ENV=test -e APP_VERSION=${BUILD_NUMBER}"
                    )
                    
                    // Wait for application to start
                    sleep(time: 10, unit: 'SECONDS')
                    
                    // Health check
                    sh '''
                        curl -f http://localhost:5000/health || exit 1
                        echo "Application deployed successfully!"
                    '''
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                script {
                    echo 'Running integration tests...'
                    sh '''
                        # Test the deployed application
                        response=$(curl -s http://localhost:5000/)
                        echo "Response: $response"
                        
                        # Check if response contains expected message
                        if echo "$response" | grep -q "Hello from CI/CD Pipeline!"; then
                            echo "Integration test passed!"
                        else
                            echo "Integration test failed!"
                            exit 1
                        fi
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
            // Clean up workspace
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
            // You can add notifications here
        }
        failure {
            echo 'Pipeline failed!'
            // Clean up any running containers
            sh '''
                docker stop test-app || true
                docker rm test-app || true
            '''
        }
    }
}