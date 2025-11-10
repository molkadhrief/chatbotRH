pipeline {
    agent any 

    stages {
        stage('Checkout') {
            steps {
                echo '--- 1. Checkout du code ---'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '--- 2. Installation locale de Trivy et Gitleaks ---'
                // Installation locale de Trivy et Gitleaks sur l'agent hôte
                sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                sh 'curl -sfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh'
                echo '--- Installation des dépendances Python ---'
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('Code Security Scan (Gitleaks & Trivy SCA )') {
            steps {
                echo '--- 3. Secrets Scan (Gitleaks) ---'
                // Règle de blocage Gitleaks: Échec si un secret est trouvé
                sh './gitleaks detect --report-format json --report-path gitleaks-report.json --exit-code 1'
                
                echo '--- 4. SCA (Trivy fs) ---'
                // Règle de blocage Trivy SCA: Échec si CRITICAL ou HIGH sont trouvés
                sh './trivy fs --format json --output trivy-sca-report.json --exit-code 1 --severity CRITICAL,HIGH "moka miko"'
            }
        }

        stage('Docker Build & Scan') {
            // Utiliser l'agent DinD (Docker-in-Docker) pour le build et le scan Docker
            agent {
                docker {
                    image 'docker:dind'
                    args '--privileged'
                }
            }
            steps {
                script {
                    echo '--- 5. Construction de l\'image Docker (DinD) ---'
                    sh 'docker build -f Dockerfile -t chatbot-rh:latest .'
                    
                    echo '--- 6. Installation de curl et Trivy dans le conteneur DinD ---'
                    sh 'apk add --no-cache curl'
                    sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                    
                    echo '--- 7. Docker Scan (Trivy image ) ---'
                    // Règle de blocage Trivy Docker: Échec si CRITICAL ou HIGH sont trouvés
                    sh './trivy image --format json --output trivy-docker-report.json --exit-code 1 --severity CRITICAL,HIGH chatbot-rh:latest'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo '--- 8. Démarrage de l\'analyse SonarQube (SAST) ---'
                withSonarQubeEnv('sonarqube') {
                    tool 'SonarScanner'
                    sh "sonar-scanner -Dsonar.projectKey=projet-molka -Dsonar.sources=moka\\ miko -Dsonar.host.url=http://localhost:9000 -Dsonar.login=${env.SONAR_AUTH_TOKEN}"
                }
            }
        }

        stage('Quality Gate Check' ) {
            steps {
                echo '--- 9. Vérification de la Quality Gate (Blocage) ---'
                timeout(time: 15, unit: 'MINUTES') {
                    // abortPipeline: true bloque le pipeline si la Quality Gate n'est pas verte
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    post {
        always {
            echo '--- 10. Archivage des rapports de sécurité ---'
            // Archivage de tous les rapports de sécurité pour le reporting
            archiveArtifacts artifacts: '*-report.json', onlyIfSuccessful: true
            echo 'Le pipeline est terminé.'
        }
    }
}
