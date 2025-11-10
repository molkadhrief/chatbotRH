pipeline {
    // Agent par défaut pour les étapes de base (checkout, installation, scans de code)
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
                // Installation locale de Trivy et Gitleaks sur l'agent hôte
                sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                sh 'curl -sfL https://raw.githubusercontent.com/gitleaks/gitleaks/master/scripts/install.sh | sh'
                echo '--- Installation des dépendances Python ---'
                // Utilisation de guillemets doubles pour le chemin avec espace
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('Code Security Scan (Gitleaks & Trivy SCA )') {
            steps {
                echo '--- Démarrage du Secrets Scan (Gitleaks) ---'
                // --exit-code 0 et || true pour continuer même en cas de détection
                sh './gitleaks detect --report-format json --report-path gitleaks-report.json --exit-code 0 || true'
                
                echo '--- Démarrage du SCA (Trivy fs) ---'
                // Scan du système de fichiers pour les dépendances
                sh './trivy fs --format json --output trivy-sca-report.json . || true'
            }
        }

        stage('Docker Build & Scan') {
            // Utiliser l'agent DinD (Docker-in-Docker) pour le build et le scan Docker
            agent {
                docker {
                    image 'docker:dind'
                    // Le mode privilégié est nécessaire pour que le conteneur puisse démarrer le démon Docker interne
                    args '--privileged'
                }
            }
            steps {
                script {
                    // 1. Construction de l'image
                    echo '--- Construction de l\'image Docker (DinD) ---'
                    // Utilisation de -f Dockerfile pour être explicite
                    sh 'docker build -f Dockerfile -t chatbot-rh:latest .'
                    
                    // 2. Installation de Trivy dans le conteneur DinD (nécessaire pour le scan)
                    echo '--- Installation de Trivy dans le conteneur DinD ---'
                    // Réinstallation car l'environnement DinD est isolé de l'agent hôte
                    sh 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest'
                    
                    // 3. Scan de l'image
                    echo '--- Démarrage du Docker Scan (Trivy image ) ---'
                    sh './trivy image --format json --output trivy-docker-report.json chatbot-rh:latest || true'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo '--- Démarrage de l\'analyse SonarQube ---'
                // 'sonarqube' est le nom de la configuration du serveur dans Jenkins
                withSonarQubeEnv('sonarqube') {
                    tool 'SonarScanner'
                    // Utilisation de guillemets doubles pour le chemin avec espace
                    sh "sonar-scanner -Dsonar.projectKey=projet-molka -Dsonar.sources=moka\\ miko -Dsonar.host.url=http://localhost:9000 -Dsonar.login=${env.SONAR_AUTH_TOKEN}"
                }
            }
        }

        stage('Quality Gate Check' ) {
            steps {
                echo '--- Vérification de la Quality Gate ---'
                // Attend le résultat de l'analyse SonarQube
                timeout(time: 15, unit: 'MINUTES') {
                    // abortPipeline: true fera échouer le pipeline si la Quality Gate n'est pas verte
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
