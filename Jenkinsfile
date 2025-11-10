pipeline {
    agent any

    stages {
        // ... (Stage Checkout inchangé) ...

        stage('Install Dependencies') {
            steps {
                // CORRECTION : Installation de Trivy dans le répertoire local (./trivy)
                sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                
                // Installation de Gitleaks (si vous l'avez gardé )
                sh 'curl -sfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh'
                
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('Security Scan' ) {
            steps {
                script {
                    echo '--- Démarrage du Secrets Scan (Gitleaks) ---'
                    // Exécution de Gitleaks
                    sh './gitleaks detect --report-format json --report-path gitleaks-report.json --exit-code 0 || true'
                    
                    echo '--- Démarrage du SCA (Trivy) ---'
                    // Exécution de Trivy pour scanner les dépendances Python (requirements.txt)
                    // Nous utilisons './trivy' car il est installé localement
                    sh './trivy fs --format json --output trivy-sca-report.json . || true'
                    
                    // Si vous utilisez Docker, ajoutez cette étape :
                    // echo '--- Démarrage du Docker Scan (Trivy) ---'
                    // sh './trivy image --format json --output trivy-docker-report.json mon_image_a_scanner:latest || true'
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
