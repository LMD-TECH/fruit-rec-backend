pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'fruit-rec-backend:1.0'
        DOCKER_CONTAINER = 'fruit-rec-backend-container'
        SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=30
        UPLOADS_DIR=static/uploads
        STATIC_DIR=static
        APP_URL = "https://fruit-rec-frontend.vercel.app"
        PORT_SMTP=587
        SMTP_SERVER_ADDR=fruit-rec-app@codeangel.pro
        SMTP_HOST=mail.codeangel.pro
        SMTP_PASSWORD=kN2@R9psGHtJgv7
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
