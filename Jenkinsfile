pipeline {
    agent any

    tools {
        // La syntaxe correcte pour déclarer l'outil SonarQube Scanner
        hudson.plugins.sonar.SonarRunnerInstallation 'SonarScanner'
    }

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
                withSonarQubeEnv('sonarqube') {
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
