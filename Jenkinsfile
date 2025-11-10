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
                    
                    // Le withSonarQubeEnv doit maintenant injecter le token
                    // car il est lié dans la configuration du serveur Jenkins.
                    withSonarQubeEnv('sonarqube') { 
                        sh "${scannerHome}/bin/sonar-scanner" 
                    }
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                // Cette étape utilise le token injecté par la configuration du serveur
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
