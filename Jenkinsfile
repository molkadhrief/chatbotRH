pipeline {
    agent any 

    environment {
        SONAR_TOKEN = credentials('sonar-token-id')
    }

    stages {
        stage('Checkout') {
            steps {
                echo '🔍 1. Checkout du code source'
                checkout scm
            }
        }

        stage('Install Security Tools') {
            steps {
                echo '🛠️ 2. Installation de Trivy et Gitleaks'
                script {
                    // Installation Trivy
                    sh '''
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest
                        ./trivy --version
                    '''
                    
                    // Installation Gitleaks
                    sh '''
                        curl -L -o gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.29.0/gitleaks_8.29.0_linux_x64.tar.gz
                        tar -xzf gitleaks.tar.gz
                        chmod +x gitleaks
                        ./gitleaks version
                    '''
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse SonarQube'
                script {
                    // Configuration SonarScanner avec l'outil Jenkins
                    withSonarQubeEnv('sonarqube') {
                        // Utiliser l'outil SonarScanner configuré dans Jenkins
                        tool 'SonarScanner'
                        sh """
                            sonar-scanner \
                            -Dsonar.projectKey=projet-molka \
                            -Dsonar.projectName="Chatbot RH" \
                            -Dsonar.projectVersion=1.0 \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=http://localhost:9000 \
                            -Dsonar.login=${SONAR_TOKEN} \
                            -Dsonar.python.version=3 \
                            -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }

        stage('Secrets Detection') {
            steps {
                echo '🔐 4. Détection des secrets - Gitleaks'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 0'
                    }
                }
            }
        }

        stage('SCA - Dependency Scan') {
            steps {
                echo '📦 5. SCA - Scan des dépendances - Trivy'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './trivy fs --format json --output trivy-sca-report.json --exit-code 0 --severity CRITICAL,HIGH .'
                    }
                }
            }
        }
    }

    post {
        always {
            echo '📊 Archivage des rapports de sécurité'
            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
        }
        success {
            echo '🎉 SUCCÈS! Pipeline DevSecOps complet!'
        }
    }
}