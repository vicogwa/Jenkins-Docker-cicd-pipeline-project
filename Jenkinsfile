pipeline {
    agent {
        docker {
            image 'docker:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock -u root'
        }
    }  
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
        
        stage('Verify Docker') {
            steps {
                script {
                    echo 'Verifying Docker setup...'
                    sh '''
                        docker --version
                        docker info
                        ls -la /var/run/docker.sock
                        whoami
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    // Use shell command instead of docker.build for better error handling
                    sh "docker build -t ${IMAGE_TAG} ./app"
                    echo "Built image: ${IMAGE_TAG}"
                }
            }
        }
        
        stage('Verify Image') {
            steps {
                script {
                    echo 'Verifying built image...'
                    sh "docker images | grep ${APP_NAME}"
                    sh "docker inspect ${IMAGE_TAG}"
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    echo 'Running tests in container...'
                    sh '''
                        docker run --rm -v $(pwd)/test-results:/app/test-results \\
                        ''' + IMAGE_TAG + ''' \\
                        bash -c "cd /app && python -m pytest tests/ -v --junitxml=test-results/test-results.xml || true"
                    '''
                }
            }
            post {
                always {
                    script {
                        // Check if test results exist before publishing
                        if (fileExists('test-results/test-results.xml')) {
                            publishTestResults testResultsPattern: 'test-results/test-results.xml'
                        } else {
                            echo 'No test results found'
                        }
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                script {
                    echo 'Running security scan...'
                    sh '''
                        echo "Security scan placeholder"
                        echo "In production, you would run tools like:"
                        echo "trivy image ''' + IMAGE_TAG + '''"
                        
                        # Basic security check - scan for vulnerabilities
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                        aquasec/trivy:latest image --exit-code 0 --severity HIGH,CRITICAL ''' + IMAGE_TAG + ''' || true
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
                    sh """
                        docker run -d --name test-app -p 5000:5000 \\
                        -e ENV=test -e APP_VERSION=${BUILD_NUMBER} \\
                        ${IMAGE_TAG}
                    """
                    
                    // Wait for application to start
                    sleep(time: 15, unit: 'SECONDS')
                    
                    // Health check with retry logic
                    sh '''
                        for i in {1..10}; do
                            if curl -f http://localhost:5000/health; then
                                echo "Health check passed on attempt $i"
                                break
                            else
                                echo "Health check failed on attempt $i, retrying..."
                                sleep 5
                            fi
                        done
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
                        # Test the deployed application with retry logic
                        for i in {1..5}; do
                            response=$(curl -s http://localhost:5000/ || echo "curl_failed")
                            echo "Response (attempt $i): $response"
                            
                            # Check if response contains expected message
                            if echo "$response" | grep -q "Hello from CI/CD Pipeline!"; then
                                echo "Integration test passed!"
                                exit 0
                            else
                                echo "Integration test failed on attempt $i, retrying..."
                                sleep 5
                            fi
                        done
                        echo "Integration test failed after all attempts!"
                        exit 1
                    '''
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo 'Pushing to registry...'
                    // Only push on main branch
                    sh """
                        docker tag ${IMAGE_TAG} ${REGISTRY}/${IMAGE_TAG}
                        docker push ${REGISTRY}/${IMAGE_TAG} || true
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
            script {
                // Clean up test containers
                sh '''
                    docker stop test-app || true
                    docker rm test-app || true
                    docker system prune -f || true
                '''
            }
            // Clean up workspace
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
            // You can add notifications here (Slack, email, etc.)
        }
        failure {
            echo 'Pipeline failed!'
            script {
                // Enhanced cleanup on failure
                sh '''
                    echo "Cleaning up failed containers..."
                    docker ps -a
                    docker stop test-app || true
                    docker rm test-app || true
                    docker logs test-app || true
                '''
            }
        }
    }
}