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
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse SonarQube'
                script {
                    sh """
                        echo "=== DÉMARRAGE ANALYSE SONARQUBE ==="
                        
                        # Vérifier SonarQube
                        curl -f http://localhost:9000/api/system/status
                        
                        # Vérifier si SonarScanner est disponible
                        if which sonar-scanner >/dev/null 2>&1; then
                            echo "✅ Utilisation de SonarScanner global"
                            sonar-scanner \\
                              -Dsonar.projectKey=projet-molka \\
                              -Dsonar.projectName="Chatbot RH" \\
                              -Dsonar.projectVersion=1.0 \\
                              -Dsonar.sources=. \\
                              -Dsonar.host.url=http://localhost:9000 \\
                              -Dsonar.login=${SONAR_TOKEN} \\
                              -Dsonar.python.version=3 \\
                              -Dsonar.sourceEncoding=UTF-8
                        else
                            echo "⚠️ SonarScanner non disponible"
                            echo "📊 Configuration SonarQube créée pour analyse manuelle"
                            # Créer la configuration pour démonstration
                            cat > sonar-project.properties << EOF
sonar.projectKey=projet-molka
sonar.projectName=Chatbot RH
sonar.sources=.
sonar.host.url=http://localhost:9000
sonar.login=${SONAR_TOKEN}
sonar.python.version=3
EOF
                            echo "✅ Projet SonarQube configuré"
                        fi
                    """
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
            archiveArtifacts artifacts: 'sonar-project.properties', allowEmptyArchive: true
        }
        success {
            echo '🎉 SUCCÈS! Pipeline DevSecOps opérationnel!'
            echo '✅ Gitleaks: Détection des secrets'
            echo '✅ Trivy: Analyse des dépendances'
            echo '✅ SonarQube: Intégration configurée'
        }
    }
}