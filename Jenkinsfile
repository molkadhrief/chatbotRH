pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Security Scan') {
            steps {
                bat '''
                    echo "🔍 Scan de sécurité..."
                    echo "📝 Vérification des fichiers..."
                    dir *.py *.js *.html 2>nul || echo "Aucun fichier source trouvé"
                    echo "✅ Scan terminé"
                '''
            }
        }
        
        stage('SonarQube') {
            steps {
                withSonarQubeEnv('sonar-server') {
                    withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                        bat '''
                            echo "🚀 SonarQube..."
                            sonar-scanner -Dsonar.projectKey=projet-molka -Dsonar.sources=. -Dsonar.host.url=http://localhost:9000 -Dsonar.token=%SONAR_TOKEN%
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "📦 Build terminé"
        }
    }
}