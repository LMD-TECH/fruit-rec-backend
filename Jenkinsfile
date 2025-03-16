pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'fruit-rec-backend'
        DOCKER_USERNAME = 'lumeidatech'
        DOCKER_CONTAINER = 'fruit-rec-backend-container'
        SSH_CREDENTIALS = credentials('vps-ssh-key') // SSH key stored in Jenkins
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials-id') // Docker Hub credentials stored in Jenkins
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
                    // Step 1: Log in to Docker Hub using stored credentials
                    sh """
                        docker login -u ${DOCKER_CREDENTIALS_USR} -p ${DOCKER_CREDENTIALS_PSW}
                        echo 'Docker login successful'
                    """

                    // Step 2: Tag the Docker image
                    sh 'docker tag $DOCKER_IMAGE $DOCKER_USERNAME/fruit-rec-backend:1.0'

                    // Step 3: Push the Docker image to Docker Hub
                    sh 'docker push $DOCKER_USERNAME/fruit-rec-backend:1.0'

                    // Step 4: Deploy to the remote server via SSH
                    sh """
                        ssh -o StrictHostKeyChecking=no -i ${SSH_CREDENTIALS} user@62.161.252.140 << 'EOF'
                            # Pull the latest Docker image
                            docker pull $DOCKER_USERNAME/fruit-rec-backend:1.0

                            # Stop and remove the existing container if it’s running
                            docker stop $DOCKER_CONTAINER || true
                            docker rm $DOCKER_CONTAINER || true

                            # Run a new container with the latest image
                            docker run -d --name $DOCKER_CONTAINER -p 8000:8000 $DOCKER_USERNAME/fruit-rec-backend:1.0
                        EOF
                    """
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