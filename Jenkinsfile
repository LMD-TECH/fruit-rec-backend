pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'fruit-rec-backend:1.0'
        DOCKER_CONTAINER = 'fruit-rec-backend-container'
        SSH_CREDENTIALS = credentials('vps-ssh-key')
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials-id')
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/LMD-TECH/fruit-rec-backend.git'
            }
        }
        stage('Test') {
            steps {
                script {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        rm -f db_test.db
                        pytest -v
                        rm -f db_test.db
                    '''
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    sh 'docker build -t $DOCKER_IMAGE .'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Push Docker Image to Docker Hub
                    sh 'docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD'
                    sh 'docker tag $DOCKER_IMAGE $DOCKER_USERNAME/fruit-rec-backend:1.0'
                    sh 'docker push $DOCKER_USERNAME/fruit-rec-backend:1.0'

                    // SSH into VPS, pull the image, and run the container
                    sh '''
                ssh -o StrictHostKeyChecking=no -i $SSH_KEY_PATH user@62.161.252.140 << 'EOF'
                    docker pull $DOCKER_USERNAME/fruit-rec-backend:1.0
                    docker stop $DOCKER_CONTAINER || true
                    docker rm $DOCKER_CONTAINER || true
                    docker run --name $DOCKER_CONTAINER -p 8000:8000 $DOCKER_USERNAME/fruit-rec-backend:1.0
                EOF
            '''
                }
            }
        }
    }

    post {
        success {
            emailext(
                subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                         <p>Check console output at <a href="${env.BUILD_URL}">${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                to: 'lumeida.tech0@gmail.com',
                mimeType: 'text/html'
            )
        }
        failure {
            emailext(
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                         <p>Check console output at <a href="${env.BUILD_URL}">${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                to: 'lumeida.tech0@gmail.com',
                mimeType: 'text/html'
            )
        }
    }
}
