pipeline {
    agent any 

    stages {
        stage('Checkout') {
            steps {
                echo '--- Checkout du code ---'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '--- Installation locale de Trivy et Gitleaks ---'
                sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                sh 'curl -sfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh'
                echo '--- Installation des dépendances Python ---'
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('Code Security Scan (Gitleaks & Trivy SCA )') {
            steps {
                echo '--- Démarrage du Secrets Scan (Gitleaks) ---'
                // Règle de blocage Gitleaks: Échec si un secret est trouvé (--exit-code 1)
                sh './gitleaks detect --report-format json --report-path gitleaks-report.json --exit-code 1'
                
                echo '--- Démarrage du SCA (Trivy fs) ---'
                // Règle de blocage Trivy SCA: Échec si CRITICAL ou HIGH sont trouvés
                sh './trivy fs --format json --output trivy-sca-report.json --exit-code 1 --severity CRITICAL,HIGH .'
            }
        }

        stage('Docker Build & Scan') {
            agent {
                docker {
                    image 'docker:dind'
                    args '--privileged'
                }
            }
            steps {
                script {
                    echo '--- Construction de l\'image Docker (DinD) ---'
                    sh 'docker build -f Dockerfile -t chatbot-rh:latest .'
                    
                    echo '--- Installation de curl et Trivy dans le conteneur DinD ---'
                    sh 'apk add --no-cache curl'
                    sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                    
                    echo '--- Démarrage du Docker Scan (Trivy image ) ---'
                    // Règle de blocage Trivy Docker: Échec si CRITICAL ou HIGH sont trouvés
                    sh './trivy image --format json --output trivy-docker-report.json --exit-code 1 --severity CRITICAL,HIGH chatbot-rh:latest'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo '--- Démarrage de l\'analyse SonarQube ---'
                withSonarQubeEnv('sonarqube') {
                    tool 'SonarScanner'
                    sh "sonar-scanner -Dsonar.projectKey=projet-molka -Dsonar.sources=moka\\ miko -Dsonar.host.url=http://localhost:9000 -Dsonar.login=${env.SONAR_AUTH_TOKEN}"
                }
            }
        }

        stage('Quality Gate Check' ) {
            steps {
                echo '--- Vérification de la Quality Gate ---'
                timeout(time: 15, unit: 'MINUTES') {
                    // abortPipeline: true est maintenu pour le blocage final par SonarQube
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    post {
        always {
            // Archivage de tous les rapports de sécurité pour le reporting
            echo '--- Archivage des rapports de sécurité ---'
            archiveArtifacts artifacts: '*-report.json', onlyIfSuccessful: true
            echo 'Le pipeline est terminé.'
        }
    }
}
