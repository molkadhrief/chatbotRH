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
                echo '🛠️ 2. Installation des outils de sécurité'
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
                    
                    // Installation SonarScanner avec CURL
                    sh '''
                        # Télécharger avec curl (plus fiable que wget)
                        curl -L -o sonar-scanner.zip "https://github.com/SonarSource/sonar-scanner-cli/releases/download/4.8.0.2856/sonar-scanner-cli-4.8.0.2856-linux.zip"
                        
                        # Installer unzip
                        apt-get update && apt-get install -y unzip
                        
                        unzip -q sonar-scanner.zip
                        chmod +x sonar-scanner-4.8.0.2856-linux/bin/sonar-scanner
                        sonar-scanner-4.8.0.2856-linux/bin/sonar-scanner --version
                    '''
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse de sécurité du code source'
                script {
                    sh """
                        sonar-scanner-4.8.0.2856-linux/bin/sonar-scanner \
                        -Dsonar.projectKey=projet-molka \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.login=${SONAR_TOKEN} \
                        -Dsonar.python.version=3
                    """
                }
            }
        }

        stage('Secrets Detection') {
            steps {
                echo '🔐 4. Détection des secrets dans le code'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 1'
                    }
                }
            }
        }

        stage('SCA - Dependency Scan') {
            steps {
                echo '📦 5. SCA - Scan des vulnérabilités des dépendances'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './trivy fs --format json --output trivy-sca-report.json --exit-code 1 --severity CRITICAL,HIGH .'
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
            echo 'Pipeline terminé!'
        }
        success {
            echo '✅ SUCCÈS! SonarQube devrait avoir des données maintenant!'
        }
    }
}