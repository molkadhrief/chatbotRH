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
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube') { 
                    // 1. Lancer l'analyse
                    sh 'sonar-scanner' 
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                // 2. ATTENDRE le résultat de la Quality Gate de SonarQube
                // Cette étape va bloquer le pipeline jusqu'à ce que SonarQube
                // ait traité l'analyse et renvoyé le statut (PASSED ou FAILED).
                waitForQualityGate abortPipeline: true
            }
        }
    }

    post {
        always {
            echo 'Le pipeline est terminé.'
        }
    }
}
