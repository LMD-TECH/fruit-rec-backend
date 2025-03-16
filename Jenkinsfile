// Déclaration du pipeline Jenkins
pipeline {
    // Exécute le pipeline sur n'importe quel agent disponible
    agent any

    // Définition des variables d'environnement globales
    environment {
        DOCKER_IMAGE = 'fruit-rec-api'  // Nom de l'image Docker à construire
        DOCKER_USERNAME = 'lumeidatech'  // Nom d'utilisateur Docker Hub
        DOCKER_CONTAINER = 'fruit-rec-api-container'  // Nom du conteneur déployé
        SSH_CREDENTIALS = credentials('vps-ssh-key')  // Clé SSH stockée dans Jenkins pour l'accès au serveur
        DOCKER_CREDENTIALS = credentials('docker-hub-credentials-id')  // Identifiants Docker Hub stockés dans Jenkins
        IMAGE_VERSION = "1.${BUILD_NUMBER}"  // Version dynamique de l'image basée sur le numéro de build Jenkins
    }

    // Définition des étapes du pipeline
    stages {
        // Étape 1 : Récupération du code source depuis GitHub
        stage('Checkout') {
            steps {
                // Clone la branche 'main' du dépôt Git spécifié
                git branch: 'main', url: 'https://github.com/LMD-TECH/fruit-rec-backend.git'
            }
        }

        // Étape 2 : Exécution des tests unitaires
        stage('Test') {
            steps {
                script {
                    // Script shell pour configurer l'environnement virtuel et exécuter les tests
                    sh '''
                        # Crée un environnement virtuel Python
                        python3 -m venv venv
                        # Active l'environnement virtuel
                        . venv/bin/activate
                        # Installe les dépendances du projet
                        pip install -r requirements.txt
                        # Supprime la base de données de test si elle existe
                        rm -f db_test.db
                        # Exécute les tests avec Pytest en mode verbeux
                        pytest -v
                        # Nettoie en supprimant la base de données de test
                        rm -f db_test.db
                    '''
                }
            }
        }

        // Étape 3 : Construction de l'image Docker
        stage('Build') {
            steps {
                script {
                    // Construit l'image Docker localement avec le nom défini dans DOCKER_IMAGE
                    sh 'docker build -t $DOCKER_IMAGE .'
                }
            }
        }

        // Étape 4 : Déploiement de l'image sur Docker Hub et sur le serveur distant
        stage('Deploy') {
            steps {
                script {
                    // Connexion à Docker Hub avec les identifiants sécurisés
                    sh """
                        # Authentification sur Docker Hub en utilisant les credentials Jenkins
                        docker login -u ${DOCKER_CREDENTIALS_USR} -p ${DOCKER_CREDENTIALS_PSW}
                        # Confirmation de la connexion réussie
                        echo 'Docker login successful'
                    """

                    // Étiquetage de l'image avec la version dynamique
                    sh """
                        # Tag l'image construite avec le nom d'utilisateur et la version
                        docker tag $DOCKER_IMAGE $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                    """

                    // Publication de l'image sur Docker Hub
                    sh """
                        # Pousse l'image taggée vers le registre Docker Hub
                        docker push $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                    """

                    // Déploiement sur le serveur distant via SSH
                    sh """
                        # Connexion SSH avec mode verbeux pour débogage
                        # Utilise la clé SSH stockée dans Jenkins pour se connecter à ubuntu@62.161.252.140
                        ssh -v -o StrictHostKeyChecking=no -i ${SSH_CREDENTIALS} ubuntu@62.161.252.140 << 'EOF'
                            # Télécharge l'image Docker spécifique depuis Docker Hub
                            docker pull $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                            # Arrête le conteneur existant s'il est en cours d'exécution (ignore les erreurs)
                            docker stop $DOCKER_CONTAINER || true
                            # Supprime le conteneur existant (ignore les erreurs)
                            docker rm $DOCKER_CONTAINER || true
                            # Lance un nouveau conteneur en mode détaché avec le port 8000 exposé
                            docker run -d --name $DOCKER_CONTAINER -p 8000:8000 $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}
                        EOF
                    """
                }
            }
        }
    }

    // Actions post-exécution du pipeline
    post {
        // Exécuté si le pipeline réussit
        success {
            // Envoie un email de confirmation avec les détails du déploiement
            emailext(
                subject: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: """<p>SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]':</p>
                         <p>Deployed image: $DOCKER_USERNAME/fruit-rec-api:${IMAGE_VERSION}</p>
                         <p>Check console output at <a href="${env.BUILD_URL}">${env.JOB_NAME} [${env.BUILD_NUMBER}]</a></p>""",
                to: 'lumeida.tech0@gmail.com',
                mimeType: 'text/html'
            )
        }

        // Exécuté si le pipeline échoue
        failure {
            // Envoie un email d'alerte avec un lien vers les logs
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