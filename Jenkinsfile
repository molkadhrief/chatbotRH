pipeline {
    agent any

    // PAS DE SECTION 'tools' ICI. On la supprime.

    stages {
        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub.'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r moka miko/requirements.txt --no-cache-dir'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // On utilise directement la commande 'withSonarQubeEnv'
                // 'sonarqube' est le nom du serveur que nous avons configuré dans Jenkins
                withSonarQubeEnv('sonarqube') { 
                    // On lance directement le scanner. Jenkins le trouvera.
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
