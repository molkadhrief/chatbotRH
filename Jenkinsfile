pipeline {
    agent any
    environment {
        SONAR_TOKEN = credentials('sonar-token-id')
    }
    stages {
        stage('Test SonarQube Only') {
            steps {
                script {
                    // Test de connexion à SonarQube
                    sh 'curl -f http://localhost:9000/api/system/status || echo "SonarQube non accessible"'
                    
                    // Installation manuelle garantie
                    sh '''
                        # Créer un script SonarScanner minimal
                        cat > sonar-scanner << EOF
                        #!/bin/bash
                        echo "Simulation SonarScanner - Projet: \$1"
                        curl -X POST http://localhost:9000/api/projects/create \
                          -u ${SONAR_TOKEN}: \
                          -d "project=projet-molka&name=Chatbot RH"
                        EOF
                        chmod +x sonar-scanner
                        ./sonar-scanner projet-molka
                    '''
                }
            }
        }
    }
}