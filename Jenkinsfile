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
                script {
                    // Installation de Trivy
                    sh '''
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest
                        ./trivy --version
                    '''
                    
                    // Installation FIXÉE de Gitleaks - méthode directe
                    sh '''
                        # Téléchargement direct de Gitleaks
                        GITLEAKS_VERSION=$(curl -s https://api.github.com/repos/gitleaks/gitleaks/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\\1/')
                        curl -L https://github.com/gitleaks/gitleaks/releases/download/${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz -o gitleaks.tar.gz
                        tar -xzf gitleaks.tar.gz
                        chmod +x gitleaks
                        ./gitleaks version
                    '''
                }
                echo '--- Installation des dépendances Python ---'
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir --user'
            }
        }

        stage('Code Security Scan (Gitleaks & Trivy SCA)') {
            steps {
                echo '--- 3. Secrets Scan (Gitleaks) ---'
                script {
                    // Gitleaks avec gestion d'erreur
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 1'
                    }
                }
                
                echo '--- 4. SCA (Trivy fs) ---'
                script {
                    // Trivy avec gestion d'erreur
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './trivy fs --format json --output trivy-sca-report.json --exit-code 1 --severity CRITICAL,HIGH "moka miko"'
                    }
                }
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
                    
                    echo '--- 7. Docker Scan (Trivy image) ---'
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './trivy image --format json --output trivy-docker-report.json --exit-code 1 --severity CRITICAL,HIGH chatbot-rh:latest'
                    }
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

        stage('Quality Gate Check') {
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
            // Archivage de tous les rapports de sécurité même si le build est unstable
            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
            echo 'Le pipeline est terminé.'
        }
        success {
            echo '✅ Build réussi!'
        }
        failure {
            echo '❌ Build échoué!'
        }
        unstable {
            echo '⚠️ Build instable - Vérifiez les rapports de sécurité'
        }
    }
}