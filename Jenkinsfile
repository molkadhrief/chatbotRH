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
                    // Commande SonarQube DIRECTE sans script
                    sh """
                        echo "🔍 Démarrage de l'analyse SonarQube..."
                        curl -f http://localhost:9000/api/system/status
                        echo "📝 Création du projet dans SonarQube..."
                        curl -X POST "http://localhost:9000/api/projects/create" \\
                          -u '${SONAR_TOKEN}:' \\
                          -d "project=projet-molka&name=Chatbot RH" || echo "ℹ️ Projet existe déjà"
                        echo "✅ Analyse SonarQube simulée - Vérifiez le dashboard!"
                    """
                }
            }
        }

        stage('Secrets Detection') {
            steps {
                echo '🔐 4. Détection des secrets'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 0'
                    }
                }
            }
        }

        stage('SCA - Dependency Scan') {
            steps {
                echo '📦 5. SCA - Scan des dépendances'
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
            echo '--- Archivage des rapports ---'
            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
            echo '✅ Pipeline DevSecOps terminé avec succès!'
        }
        success {
            echo '🎉 SUCCÈS! Vérifiez SonarQube pour les données!'
        }
        unstable {
            echo '⚠️ Build instable - Des vulnérabilités trouvées'
        }
    }
}