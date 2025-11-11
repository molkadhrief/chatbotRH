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
                sh '''
                    echo "🔍 Scan de sécurité Linux..."
                    echo "📁 Structure du projet:"
                    find . -type f -name "*.py" -o -name "*.js" -o -name "*.html" | head -10
                    echo "✅ Scan basique terminé"
                '''
            }
        }
        
        stage('SonarQube') {
            steps {
                withSonarQubeEnv('sonar-server') {
                    withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                        sh '''
                            echo "🚀 SonarQube..."
                            sonar-scanner \
                            -Dsonar.projectKey=projet-molka \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=http://localhost:9000 \
                            -Dsonar.token=${SONAR_TOKEN}
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "📦 Build terminé sur Linux"
        }
    }
}