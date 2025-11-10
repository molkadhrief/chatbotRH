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
                    // 1. Localise l'installation de SonarScanner
                    def scannerHome = tool 'SonarScanner' 
                    
                    // 2. INJECTION DIRECTE DU JETON EXISTANT
                    // L'ID 'sonar-token-id' doit correspondre à l'ID qui existe déjà dans Jenkins.
                    withCredentials([string(credentialsId: 'sonar-token-id', variable: 'SONAR_TOKEN')]) {
                        withSonarQubeEnv('sonarqube') { 
                            // 3. Exécute le scanner. Il utilisera la variable SONAR_TOKEN injectée.
                            sh "${scannerHome}/bin/sonar-scanner" 
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                // 4. Attend le résultat de l'analyse
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
