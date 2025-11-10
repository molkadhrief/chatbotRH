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
                        wget -q https://github.com/gitleaks/gitleaks/releases/download/v8.29.0/gitleaks_8.29.0_linux_x64.tar.gz
                        tar -xzf gitleaks_8.29.0_linux_x64.tar.gz
                        chmod +x gitleaks
                        ./gitleaks version
                    '''
                    
                    // Installation SonarScanner - NOUVELLE URL GARANTIE
                    sh '''
                        # Télécharger depuis une source fiable
                        wget -q https://github.com/SonarSource/sonar-scanner-cli/releases/download/4.8.0.2856/sonar-scanner-cli-4.8.0.2856-linux.zip
                        
                        # Installer unzip si nécessaire
                        which unzip || (apt-get update && apt-get install -y unzip)
                        
                        unzip -q sonar-scanner-cli-4.8.0.2856-linux.zip
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
                        -Dsonar.login=${SONAR_TOKEN}
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
            echo '--- Archivage des rapports de sécurité ---'
            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
            echo 'Le pipeline DevSecOps est terminé.'
        }
        success {
            echo '✅ Build réussi! - SonarQube devrait maintenant avoir des données!'
        }
        failure {
            echo '❌ Build échoué!'
        }
        unstable {
            echo '⚠️ Build instable - Des vulnérabilités ont été trouvées'
        }
    }
}