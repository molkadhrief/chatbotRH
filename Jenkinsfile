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
                    def scannerHome = tool 'SonarScanner' 
                    
                    // INJECTION DIRECTE DU JETON EXISTANT (ID: sonar-token-id)
                    // Cette méthode force l'injection du jeton dans l'environnement du scanner.
                    withCredentials([string(credentialsId: 'sonar-token-id', variable: 'SONAR_TOKEN')]) {
                        withSonarQubeEnv('sonarqube') { 
                            sh "${scannerHome}/bin/sonar-scanner" 
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                // Cette étape va probablement échouer à nouveau avec 401,
                // car elle ne bénéficie pas de l'injection withCredentials.
                // Mais nous devons d'abord réussir l'analyse.
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
