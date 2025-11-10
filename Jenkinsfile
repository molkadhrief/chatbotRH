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
                script {
                    // CORRECTION FINALE : Utilisation du nom exact de l'outil configuré dans Jenkins
                    def scannerHome = tool 'SonarScanner' 
                    
                    withSonarQubeEnv('sonarqube') { 
                        // Lancement de l'analyse via le chemin complet de l'exécutable
                        sh "${scannerHome}/bin/sonar-scanner" 
                    }
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                // ATTENDRE le résultat de la Quality Gate de SonarQube
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
