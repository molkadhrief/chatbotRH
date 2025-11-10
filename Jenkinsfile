        stage('Docker Build & Scan') {
            agent {
                docker {
                    image 'docker:dind'
                    args '--privileged'
                }
            }
            steps {
                script {
                    // 1. Construction de l'image
                    echo '--- Construction de l\'image Docker (DinD) ---'
                    sh 'docker build -f Dockerfile -t chatbot-rh:latest .'
                    
                    // 2. Installation des dépendances pour le scan (curl, puis Trivy)
                    echo '--- Installation de curl et Trivy dans le conteneur DinD ---'
                    // L'image docker:dind est basée sur Alpine, nous utilisons donc 'apk'
                    sh 'apk add --no-cache curl'
                    sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                    
                    // 3. Scan de l'image
                    echo '--- Démarrage du Docker Scan (Trivy image ) ---'
                    sh './trivy image --format json --output trivy-docker-report.json chatbot-rh:latest || true'
                }
            }
        }
