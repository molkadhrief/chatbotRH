pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub.'
            }
        }

        stage('Install Dependencies') {
            steps {
                // Le chemin est correctement entre guillemets
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // Utilisation de la syntaxe confirmée par le Snippet Generator
                withSonarQubeEnv('sonarqube') { 
                    // La commande simple 'sonar-scanner' suffit, car withSonarQubeEnv
                    // va préparer le chemin vers l'exécutable.
                    sh 'sonar-scanner' 
                }
            }
        }
    }

    post {
        always {
            echo 'Le pipeline est terminé.'
        }
    }
}
