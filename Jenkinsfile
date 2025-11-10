pipeline {
    // Agent par défaut pour les étapes qui n'ont pas besoin de Docker
    agent any 

    stages {
        // ... (Stage Checkout inchangé) ...

        stage('Install Dependencies') {
            steps {
                // Installation locale de Trivy et Gitleaks
                sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                sh 'curl -sfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh'
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('Build Docker Image' ) {
            // Utiliser un agent Docker pour ce stage
            agent {
                docker {
                    image 'docker:latest'
                    // Monter le socket Docker de l'hôte pour permettre la construction
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                echo '--- Construction de l\'image Docker ---'
                // La commande docker build devrait maintenant fonctionner
                sh 'docker build -t chatbot-rh:latest .'
            }
        }

        stage('Security Scan') {
            // Utiliser un agent Docker pour ce stage (pour le scan de l'image)
            agent {
                docker {
                    image 'docker:latest'
                    // Monter le socket Docker de l'hôte pour accéder à l'image construite
                    args '-v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    echo '--- Démarrage du Secrets Scan (Gitleaks) ---'
                    // Gitleaks et Trivy doivent être accessibles dans ce conteneur
                    // Pour simplifier, nous allons les installer ici aussi, ou utiliser une image plus complète.
                    
                    // Pour l'instant, nous allons revenir à l'agent 'any' pour le scan
                    // et supposer que l'image est accessible.
                    
                    // RETOUR À L'AGENT ANY POUR LE SCAN (pour éviter de réinstaller Trivy/Gitleaks)
                    // Si l'image est construite, elle devrait être accessible par l'hôte.
                    
                    // Si l'image est construite, elle est accessible par l'hôte.
                    // Nous revenons à l'agent 'any' pour le scan pour utiliser Trivy/Gitleaks installés.
                    
                    // Si le stage Build Docker Image réussit, l'image est disponible sur l'hôte.
                    // Nous pouvons revenir à l'agent 'any' pour le scan.
                    
                    echo '--- Démarrage du Secrets Scan (Gitleaks) ---'
                    sh './gitleaks detect --report-format json --report-path gitleaks-report.json --exit-code 0 || true'
                    
                    echo '--- Démarrage du SCA (Trivy) ---'
                    sh './trivy fs --format json --output trivy-sca-report.json . || true'
                    
                    echo '--- Démarrage du Docker Scan (Trivy) ---'
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
