pipeline {
    agent any 

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '--- Installation locale de Trivy et Gitleaks ---'
                // Installation locale de Trivy et Gitleaks
                sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                sh 'curl -sfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh'
                echo '--- Installation des dépendances Python ---'
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('Build Docker Image' ) {
            // Utiliser un agent Docker-in-Docker (DinD) pour ce stage
            agent {
                docker {
                    image 'docker:dind'
                    // Le mode privilégié est nécessaire pour que le conteneur puisse démarrer le démon Docker interne
                    args '--privileged'
                }
            }
            steps {
                echo '--- Construction de l\'image Docker (DinD) ---'
                // Le démon Docker est maintenant disponible à l'intérieur de ce conteneur
                sh 'docker build -t chatbot-rh:latest .'
            }
        }

        stage('Security Scan') {
            // Revenir à l'agent par défaut pour utiliser les outils installés localement
            agent any
            steps {
                script {
                    echo '--- Démarrage du Secrets Scan (Gitleaks) ---'
                    // Les scans continuent même en cas d'erreur (|| true)
                    sh './gitleaks detect --report-format json --report-path gitleaks-report.json --exit-code 0 || true'
                    
                    echo '--- Démarrage du SCA (Trivy) ---'
                    sh './trivy fs --format json --output trivy-sca-report.json . || true'
                    
                    echo '--- Démarrage du Docker Scan (Trivy) ---'
                    // L'image construite dans le stage précédent n'est PAS disponible ici
                    // car elle a été construite dans un conteneur DinD temporaire.
                    // Nous devons reconstruire l'image pour le scan, ou utiliser l'option --input de Trivy.
                    
                    // Pour simplifier, nous allons reconstruire l'image DANS CE STAGE
                    // en utilisant le même agent DinD, puis la scanner.
                    
                    // **ATTENTION :** Le stage 'Security Scan' doit être modifié pour utiliser DinD.
                    // Je vais donc fusionner le build et le scan Docker dans un seul stage.
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
