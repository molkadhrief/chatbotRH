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
                    
                    // Installation de pysonar (Scanner Python officiel)
                    sh '''
                        echo "=== INSTALLATION PYSONAR ==="
                        pip3 install pysonar --user
                        echo "✅ pysonar installé"
                    '''
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse SonarQube avec pysonar'
                script {
                    sh """
                        echo "=== DÉMARRAGE ANALYSE SONARQUBE AVEC PYSONAR ==="
                        
                        # Vérifier SonarQube
                        curl -f http://localhost:9000/api/system/status
                        
                        # Lancer l'analyse avec pysonar (commande officielle)
                        echo "🚀 Lancement de l'analyse SonarQube avec pysonar..."
                        pysonar \\
                          --sonar-host-url=http://localhost:9000 \\
                          --sonar-token=${SONAR_TOKEN} \\
                          --sonar-project-key=projet-molka
                        
                        echo "🎉 ANALYSE SONARQUBE TERMINÉE !"
                        echo "📊 Vérifiez le dashboard SonarQube pour les résultats"
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
        }
        success {
            echo '🎉 SUCCÈS! Analyse SonarQube complète avec pysonar!'
            echo '✅ SonarQube: Données affichées dans le dashboard'
            echo '✅ Gitleaks: Détection des secrets'
            echo '✅ Trivy: Scan des dépendances'
        }
    }
}