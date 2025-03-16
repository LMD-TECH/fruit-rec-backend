// Déclaration du pipeline Jenkins
pipeline {
    agent any

    // Variables d'environnement globales
    environment {
        DOCKER_IMAGE = 'fruit-rec-api'  // Nom de l'image Docker
        DOCKER_USERNAME = 'lumeidatech'  // Nom d'utilisateur Docker Hub
        DOCKER_CONTAINER = 'fruit-rec-api-container'  // Nom du conteneur sur le serveur
        SSH_CREDENTIALS = credentials('vps-ssh-key')  // Clé SSH pour l'accès au serveur distant
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials-id')  // Identifiants Docker Hub
        IMAGE_VERSION = "1.${BUILD_NUMBER}"  // Version dynamique basée sur le numéro de build
    }

    stages {
        // Étape 1 : Récupération du code source
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/LMD-TECH/fruit-rec-backend.git'
            }
        }

        // Étape 2 : Tests unitaires
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

        // Étape 3 : Construction de l'image Docker
        stage('Build') {
            steps {
                script {
                    sh 'docker build -t $DOCKER_IMAGE .'
                }
            }
        }

        // Étape 4 : Déploiement
        stage('Deploy') {
            steps {
                script {
                    // Connexion à Docker Hub sur l'agent Jenkins
                    sh """
                        docker login -u ${DOCKER_CREDENTIALS_USR} -p ${DOCKER_CREDENTIALS_PSW}
                        echo 'Docker login successful'
                    """

                    // Étiquetage de l'image
                    sh """
                        docker tag $DOCKER_IMAGE $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                    """

                    // Publication sur Docker Hub
                    sh """
                        docker push $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                    """

                    // Déploiement sur le serveur distant
                    sh """
                        ssh -v -o StrictHostKeyChecking=no -i ${SSH_CREDENTIALS} ubuntu@62.161.252.140 << 'EOF'
                            # Connexion à Docker Hub sur le serveur distant
                            docker login -u ${DOCKER_CREDENTIALS_USR} -p ${DOCKER_CREDENTIALS_PSW}
                            # Téléchargement de l'image
                            docker pull $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                            # Arrêt du conteneur existant (silencieux si absent)
                            docker stop $DOCKER_CONTAINER || true
                            # Suppression du conteneur existant (silencieux si absent)
                            docker rm $DOCKER_CONTAINER || true
                            # Lancement du nouveau conteneur
                            docker run -d --name $DOCKER_CONTAINER -p 8000:8000 $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                        EOF
                    """
                }
            }
        }
    }

    // Actions post-exécution
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