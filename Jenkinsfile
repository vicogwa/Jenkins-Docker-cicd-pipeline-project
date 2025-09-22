pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/vicogwa/Jenkins-Docker-cicd-pipeline-project'
            }
        }

        stage('Build') {
            steps {
                script {
                    node('master') {
                        echo "Building the project..."
                        sh 'docker build -t cicd-app .'
                    }
                }
            }
        }

        stage('Unit Test') {
            steps {
                script {
                    node('master') {
                        echo "Running unit tests..."
                        sh 'docker run --rm cicd-app npm test'
                    }
                }
            }
        }

        stage('Push Image') {
            steps {
                script {
                    node('master') {
                        echo "Pushing Docker image..."
                        withCredentials([usernamePassword(credentialsId: 'dockerhub', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                            sh '''
                                echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                                docker tag cicd-app $DOCKER_USERNAME/cicd-app:latest
                                docker push $DOCKER_USERNAME/cicd-app:latest
                            '''
                        }
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    node('master') {
                        echo "Deploying container..."
                        sh '''
                            docker stop cicd-app || true
                            docker rm cicd-app || true
                            docker run -d -p 8080:8080 --name cicd-app cicd-app
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            echo "Cleaning up workspace..."
            cleanWs()
        }
    }
}
