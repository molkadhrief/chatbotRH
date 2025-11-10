pipeline {
    agent any
    stages {
        stage('Test SonarQube') {
            steps {
                script {
                    echo "🔍 Test de connexion SonarQube..."
                    
                    // Test connexion
                    def status = sh(
                        script: 'curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/api/system/status || echo "000"',
                        returnStdout: true
                    ).trim()
                    
                    echo "Status HTTP SonarQube: ${status}"
                    
                    if (status == "200") {
                        echo "✅ SonarQube est accessible"
                    } else {
                        echo "❌ SonarQube n'est pas accessible (HTTP: ${status})"
                    }
                    
                    // Test SonarScanner
                    try {
                        sh 'sonar-scanner --version'
                        echo "✅ SonarScanner est installé"
                    } catch (Exception e) {
                        echo "❌ SonarScanner n'est pas installé"
                    }
                }
            }
        }
    }
}