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
                    
                    // Installation SonarScanner
                    sh '''
                        wget -q https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                        unzip -q sonar-scanner-cli-5.0.1.3006-linux.zip
                        mv sonar-scanner-5.0.1.3006-linux sonar-scanner
                        chmod +x sonar-scanner/bin/sonar-scanner
                        sonar-scanner/bin/sonar-scanner --version
                    '''
                }
                
                echo '--- Installation des dépendances Python ---'
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir --user'
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse de sécurité du code source'
                script {
                    // Commande SonarScanner avec token projet
                    sh """
                        sonar-scanner/bin/sonar-scanner \
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

        stage('Quality Gate Check') {
            steps {
                echo '🚨 6. Vérification de la Quality Gate'
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
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
            echo '✅ Build réussi! - Tous les contrôles de sécurité sont passés'
        }
        failure {
            echo '❌ Build échoué! - Des erreurs critiques ont été détectées'
        }
        unstable {
            echo '⚠️ Build instable - Des vulnérabilités de sécurité ont été trouvées'
        }
    }
}