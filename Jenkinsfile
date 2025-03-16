pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'fruit-rec-api'
        DOCKER_USERNAME = 'lumeidatech'
        DOCKER_CONTAINER = 'fruit-rec-api-container'
        SSH_CREDENTIALS = credentials('vps-ssh-key')
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials-id')
        IMAGE_VERSION = "1.${BUILD_NUMBER}"  // Dynamic version with BUILD_NUMBER
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
                    sh """
                        # Debug: Inspect the key file Jenkins provides
                        echo "SSH key file: ${SSH_CREDENTIALS}"
                        ls -l ${SSH_CREDENTIALS}
                        head -n 5 ${SSH_CREDENTIALS}
                        ssh-keygen -l -f ${SSH_CREDENTIALS}  # Show fingerprint
                    """
                    // Log in to Docker Hub
                    sh """
                        docker login -u ${DOCKER_CREDENTIALS_USR} -p ${DOCKER_CREDENTIALS_PSW}
                        echo 'Docker login successful'
                    """

                    // Tag the image with the dynamic version only
                    sh """
                        docker tag $DOCKER_IMAGE $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                    """

                    // Push the versioned tag to Docker Hub
                    sh """
                        docker push $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                    """

                    // Deploy to the remote server with the dynamic version
                    sh """

                        ssh -v -o StrictHostKeyChecking=no -i ${SSH_CREDENTIALS} user@62.161.252.140 << 'EOF'
                            docker pull $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                            docker stop $DOCKER_CONTAINER || true
                            docker rm $DOCKER_CONTAINER || true
                            docker run -d --name $DOCKER_CONTAINER -p 8000:8000 $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
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
                         <p>Deployed image: $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}</p>
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
