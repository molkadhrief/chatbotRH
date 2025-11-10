pipeline {
    agent any 

    stages {
        stage('Checkout') {
            steps {
                echo '🔍 1. Checkout du code source'
                checkout scm
            }
        }

        stage('Install Security Tools') {
            steps {
                echo '🛠️ 2. Installation des outils de sécurité'
                script {
                    // Installation Trivy
                    sh '''
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest
                        ./trivy --version
                    '''
                    
                    // Installation Gitleaks
                    sh '''
                        curl -L -o gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.29.0/gitleaks_8.29.0_linux_x64.tar.gz
                        tar -xzf gitleaks.tar.gz
                        chmod +x gitleaks
                        ./gitleaks version
                    '''
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse SonarQube'
                // UTILISER withSonarQubeEnv pour que Quality Gate fonctionne
                withSonarQubeEnv('sonar-server') {
                    script {
                        withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                            sh '''
                                echo "🚀 Lancement de l'analyse SonarQube..."
                                sonar-scanner \
                                -Dsonar.projectKey=projet-molka \
                                -Dsonar.sources=. \
                                -Dsonar.projectName="Projet Molka" \
                                -Dsonar.projectVersion=1.0 \
                                -Dsonar.host.url=http://localhost:9000 \
                                -Dsonar.token=${SONAR_TOKEN} \
                                -Dsonar.sourceEncoding=UTF-8
                            '''
                        }
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                echo '📊 4. Vérification Quality Gate'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }

        stage('Secrets Detection') {
            steps {
                echo '🔐 5. Détection des secrets - Gitleaks'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh '''
                            echo "=== DÉTECTION DES SECRETS ==="
                            ./gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 0
                            echo "✅ Scan Gitleaks terminé"
                        '''
                    }
                }
            }
        }

        stage('SCA - Dependency Scan') {
            steps {
                echo '📦 6. SCA - Scan des dépendances - Trivy'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh '''
                            echo "=== SCAN DES DÉPENDANCES ==="
                            ./trivy fs --format json --output trivy-sca-report.json --exit-code 0 --severity CRITICAL,HIGH .
                            echo "✅ Scan Trivy terminé"
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            echo '📊 Archivage des rapports de sécurité'
            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
            
            sh '''
                echo "=== NETTOYAGE ==="
                rm -f trivy gitleaks gitleaks.tar.gz *.zip
                echo "✅ Nettoyage terminé"
            '''
        }
        success {
            echo '🎉 SUCCÈS! Pipeline de sécurité terminé!'
            echo '✅ SonarQube: Analyse SAST complète'
            echo '✅ Gitleaks: Détection des secrets'
            echo '✅ Trivy: Scan des dépendances'
            echo '📊 Résultats disponibles dans SonarQube: http://localhost:9000/dashboard?id=projet-molka'
        }
        failure {
            echo '❌ ÉCHEC! Vérifiez les logs pour plus de détails'
        }
        unstable {
            echo '⚠️ Pipeline instable - Des problèmes de sécurité ont été détectés'
        }
    }
}