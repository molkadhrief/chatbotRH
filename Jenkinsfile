pipeline {
    agent any 

    stages {
        // ... (Stages Checkout, Install Dependencies, Code Security Scan inchangés) ...

        stage('Docker Build & Scan') {
            steps {
                script {
                    // 1. Construction de l'image (nécessite les permissions Docker corrigées)
                    echo '--- Construction de l\'image Docker ---'
                    sh 'docker build -t chatbot-rh:latest .'
                    
                    // 2. Scan de l'image (utilise Trivy installé dans Install Dependencies)
                    echo '--- Démarrage du Docker Scan (Trivy image) ---'
                    // Trivy est déjà dans le PATH de l'agent hôte
                    sh './trivy image --format json --output trivy-docker-report.json chatbot-rh:latest || true'
                }
            }
        }

        // ... (Stages SonarQube Analysis, Quality Gate Check, et post inchangés) ...
    }
}
