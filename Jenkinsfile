pipeline {
    agent any 

    environment {
        SONAR_TOKEN = credentials('sonar-token-id')
    }

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
                    
                    // Installation SonarScanner - SANS UNZIP
                    sh '''
                        echo "=== INSTALLATION SONARSCANNER SANS UNZIP ==="
                        # Télécharger la version .tar.gz au lieu de .zip
                        curl -L -o sonar-scanner.tar.gz "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-4.8.0.2856-linux.tar.gz"
                        
                        # Extraire avec tar (pas besoin de unzip)
                        tar -xzf sonar-scanner.tar.gz
                        mv sonar-scanner-4.8.0.2856-linux sonar-scanner
                        chmod +x sonar-scanner/bin/sonar-scanner
                        
                        echo "SonarScanner installé :"
                        sonar-scanner/bin/sonar-scanner --version
                    '''
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - ANALYSE RÉELLE SonarQube'
                script {
                    sh """
                        echo "=== DÉMARRAGE ANALYSE SONARQUBE ==="
                        
                        # Vérifier que SonarQube est accessible
                        curl -f http://localhost:9000/api/system/status
                        
                        # EXÉCUTER LA VRAIE ANALYSE
                        sonar-scanner/bin/sonar-scanner \\
                          -Dsonar.projectKey=projet-molka \\
                          -Dsonar.projectName="Chatbot RH" \\
                          -Dsonar.sources=. \\
                          -Dsonar.host.url=http://localhost:9000 \\
                          -Dsonar.login=${SONAR_TOKEN} \\
                          -Dsonar.python.version=3 \\
                          -Dsonar.sourceEncoding=UTF-8
                        
                        echo "✅ ANALYSE SONARQUBE TERMINÉE !"
                        echo "📊 Allez vérifier les résultats sur http://localhost:9000"
                    """
                }
            }
        }

        stage('Secrets Detection') {
            steps {
                echo '🔐 4. Détection des secrets - GITLEAKS'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 0'
                    }
                }
            }
        }

        stage('SCA - Dependency Scan') {
            steps {
                echo '📦 5. SCA - Scan des dépendances - TRIVY'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './trivy fs --format json --output trivy-sca-report.json --exit-code 0 --severity CRITICAL,HIGH .'
                    }
                }
            }
        }
    }

    post {
        always {
            echo '=== ARCHIVAGE DES RAPPORTS ==='
            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
            echo '✅ Pipeline DevSecOps terminé avec succès!'
        }
        success {
            echo '🎉 SUCCÈS! Analyse SonarQube complète effectuée!'
            echo '📊 Vérifiez http://localhost:9000 pour les résultats détaillés'
        }
    }
}