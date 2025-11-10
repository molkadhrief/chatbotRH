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
                // 1. Définir le nom de l'installation SonarScanner configurée dans Jenkins
                // REMPLACEZ 'MonSonarScanner' par le nom exact de votre installation SonarScanner
                def scannerHome = tool 'MonSonarScanner' 

                withSonarQubeEnv('sonarqube') { 
                    // 2. Lancer l'analyse en utilisant le chemin complet de l'exécutable
                    sh "${scannerHome}/bin/sonar-scanner" 
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                // 3. ATTENDRE le résultat de la Quality Gate de SonarQube
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
