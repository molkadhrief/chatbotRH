pipeline {
    agent any

    stages {
        // ... (Stages Checkout et Install Dependencies inchangés) ...

        stage('Build Docker Image') {
            steps {
                echo '--- Construction de l\'image Docker ---'
                // Remplacez 'chatbot-rh:latest' par le nom de votre image
                sh 'docker build -t chatbot-rh:latest .'
            }
        }

        stage('Security Scan') {
            steps {
                script {
                    echo '--- Démarrage du Secrets Scan (Gitleaks) ---'
                    sh './gitleaks detect --report-format json --report-path gitleaks-report.json --exit-code 0 || true'
                    
                    echo '--- Démarrage du SCA (Trivy) ---'
                    sh './trivy fs --format json --output trivy-sca-report.json . || true'
                    
                    echo '--- Démarrage du Docker Scan (Trivy) ---'
                    // Remplacez 'chatbot-rh:latest' par le nom de votre image
                    sh './trivy image --format json --output trivy-docker-report.json chatbot-rh:latest || true'
                }
            }
        }

        // ... (Stages SonarQube Analysis et Quality Gate Check inchangés) ...
    }

    post {
        always {
            echo 'Le pipeline est terminé.'
        }
    }
}
