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
                // Installation locale de Trivy et Gitleaks sur l'agent hôte
                sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                sh 'curl -sfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh'
                echo '--- Installation des dépendances Python ---'
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('Code Security Scan (Gitleaks & Trivy SCA )') {
            steps {
                echo '--- Démarrage du Secrets Scan (Gitleaks) ---'
                sh './gitleaks detect --report-format json --report-path gitleaks-report.json --exit-code 0 || true'
                
                echo '--- Démarrage du SCA (Trivy fs) ---'
                sh './trivy fs --format json --output trivy-sca-report.json . || true'
            }
        }

        stage('Docker Build & Scan') {
            // Utiliser l'agent DinD pour le build et le scan Docker
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
                    sh 'docker build -t chatbot-rh:latest .'
                    
                    // 2. Installation de Trivy dans le conteneur DinD (nécessaire pour le scan)
                    echo '--- Installation de Trivy dans le conteneur DinD ---'
                    sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                    
                    // 3. Scan de l'image
                    echo '--- Démarrage du Docker Scan (Trivy image ) ---'
                    // Le binaire Trivy est maintenant dans le répertoire courant du conteneur DinD
                    sh './trivy image --format json --output trivy-docker-report.json chatbot-rh:latest || true'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo '--- Démarrage de l\'analyse SonarQube ---'
                withSonarQubeEnv('sonarqube') {
                    // Utilisation de la variable d'environnement SONAR_TOKEN
                    tool 'SonarScanner'
                    sh "sonar-scanner -Dsonar.projectKey=projet-molka -Dsonar.sources=moka\\ miko -Dsonar.host.url=http://localhost:9000 -Dsonar.login=${env.SONAR_AUTH_TOKEN}"
                }
            }
        }

        stage('Quality Gate Check' ) {
            steps {
                echo '--- Vérification de la Quality Gate ---'
                // Utilisation de la fonction waitForQualityGate fournie par le plugin SonarQube
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    post {
        always {
            // Archivage des rapports de sécurité pour le reporting
            archiveArtifacts artifacts: '*-report.json', onlyIfSuccessful: true
            echo 'Le pipeline est terminé.'
        }
    }
}
