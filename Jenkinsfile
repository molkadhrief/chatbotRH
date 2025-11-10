pipeline {
    agent any

    tools {
        // Installe l'outil SonarQube Scanner, doit correspondre au nom dans Jenkins
        // Nous allons configurer ce nom "SonarScanner" dans Jenkins juste après
        tool 'SonarScanner' 
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub.'
                // Le checkout est fait automatiquement par le pipeline
            }
        }

        stage('Install Dependencies') {
            steps {
                // Utilise pip3 pour installer les dépendances
                sh 'pip3 install -r moka miko/requirements.txt --no-cache-dir'
            }
        }

        // --- NOUVELLE ÉTAPE ---
        stage('SonarQube Analysis') {
            steps {
                // Utilise l'outil SonarScanner configuré dans Jenkins
                withSonarQubeEnv('sonarqube') { // 'sonarqube' est le nom que nous donnerons au serveur dans Jenkins
                    sh '''
                        $SCANNER_HOME/bin/sonar-scanner \
                        -Dsonar.projectKey=chatbot-rh \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.token=squ_19237b74db76d95b82d9421c07925637fe3a7a01

                    '''
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
