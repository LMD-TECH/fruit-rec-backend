pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'fruit-rec-backend:1.0'
        DOCKER_CONTAINER = 'fruit-rec-backend-container'
    
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
                    sh "python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
                    sh "rm -f db_test.db && pytest -v && rm -f db_test.db"

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
                    sh 'docker run --name $DOCKER_CONTAINER -p 8000:8000 $DOCKER_IMAGE'
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
                to: 'mantsouakaarthur10@gmail.com',
                mimeType: 'text/html'
            )
        }
        failure {
            emailext(
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                         <p>Check console output at <a href="${env.BUILD_URL}">${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                to: 'mantsouakaarthur10@gmail.com',
                mimeType: 'text/html'
            )
        }
    }
}
