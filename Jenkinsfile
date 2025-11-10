pipeline {
    agent any 
    stages {
        stage('Checkout') {
            steps {
                echo '--- 1. Checkout du code ---'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                // [Vos étapes d'installation...]
            }
        }

        stage('Code Security Scan') {
            steps {
                // [Vos scans de sécurité...]
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo '--- Analyse SonarQube ---'
                script {
                    withSonarQubeEnv('sonarqube') {
                        tool 'SonarScanner'  // ← Utilise le SonarScanner configuré
                        sh """
                            sonar-scanner \
                            -Dsonar.projectKey=projet-molka \
                            -Dsonar.sources="moka miko" \
                            -Dsonar.host.url=http://localhost:9000 \
                            -Dsonar.login=${env.SONAR_AUTH_TOKEN}
                        """
                    }
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }
}