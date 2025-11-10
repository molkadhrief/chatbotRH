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
                    
                    // Installation de Gitleaks
                    sh '''
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

        stage('Code Security Scan') {
            steps {
                echo '--- 3. Secrets Scan (Gitleaks) ---'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 1'
                    }
                }
                
                echo '--- 4. SCA (Trivy fs) ---'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './trivy fs --format json --output trivy-sca-report.json --exit-code 1 --severity CRITICAL,HIGH "moka miko"'
                    }
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo '--- 5. Analyse SonarQube ---'
                script {
                    withSonarQubeEnv('sonarqube') {
                        tool 'SonarScanner'
                        sh """
                            sonar-scanner \
                            -Dsonar.projectKey=projet-molka \
                            -Dsonar.sources="moka miko" \
                            -Dsonar.host.url=http://localhost:9000 \
                            -Dsonar.login=${env.SONAR_AUTH_TOKEN}
                        """
                    }
                }
            }
        }

        stage('Quality Gate Check') {
            steps {
                echo '--- 6. Vérification Quality Gate ---'
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }

    post {
        always {
            echo '--- Archivage des rapports ---'
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