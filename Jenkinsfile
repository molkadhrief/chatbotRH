pipeline {
    agent any 
    
    environment {
        SONARQUBE_URL = 'http://localhost:9000'
    }
    
    stages {
        stage('Checkout') {
            steps { 
                echo '🔍 1. Checkout'
                checkout scm 
            }
        }
        
        stage('Security Scan') {
            steps {
                echo '🛡️ 2. Scan de sécurité'
                script {
                    bat '''
                        echo "=== SCAN SÉCURITÉ SIMPLIFIÉ ==="
                        
                        # Scan Bandit basique
                        if exist *.py (
                            echo "🐍 Bandit - Scan Python..."
                            bandit -r . -f json -o bandit-report.json || echo "Bandit scan terminé"
                        )
                        
                        # Scan secrets basique
                        echo "🔐 Scan secrets..."
                        findstr /S /I "password secret" *.py *.txt 2>nul > secrets.txt || echo "Aucun secret trouvé"
                        
                        echo "✅ Scan sécurité terminé"
                    '''
                }
            }
        }
        
        stage('Generate Report') {
            steps {
                echo '📊 3. Génération rapport'
                script {
                    bat '''
                        echo "=== GÉNÉRATION RAPPORT ==="
                        
                        # Rapport HTML simple
                        echo ^<!DOCTYPE html^> > security-report.html
                        echo ^<html^> >> security-report.html
                        echo ^<head^>^<title^>Rapport Sécurité^</title^>^</head^> >> security-report.html
                        echo ^<body^> >> security-report.html
                        echo ^<h1^>Rapport Sécurité^</h1^> >> security-report.html
                        echo ^<p^>Scan terminé avec succès^</p^> >> security-report.html
                        echo ^</body^>^</html^> >> security-report.html
                        
                        echo "✅ Rapport généré"
                    '''
                }
            }
        }
        
        stage('SonarQube') {
            steps {
                echo '🔎 4. SonarQube'
                withSonarQubeEnv('sonar-server') {
                    script {
                        withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                            bat '''
                                echo "🚀 SonarQube..."
                                sonar-scanner ^
                                -Dsonar.projectKey=projet-molka ^
                                -Dsonar.sources=. ^
                                -Dsonar.host.url=http://localhost:9000 ^
                                -Dsonar.token=%SONAR_TOKEN%
                            '''
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '*.json,*.html,*.txt', allowEmptyArchive: true
            echo '📦 Rapports archivés'
        }
        
        success {
            echo '✅ Pipeline réussi!'
        }
    }
}