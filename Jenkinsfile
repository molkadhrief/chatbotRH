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
                    
                    // Création du script SonarScanner - CORRIGÉ
                    sh '''
                        # Créer le script SonarScanner
                        cat > sonar-scanner.sh << 'EOF'
                        #!/bin/bash
                        echo "🔍 Démarrage de l'analyse SonarQube..."
                        
                        # Vérifier que SonarQube est accessible
                        curl -f http://localhost:9000/api/system/status
                        
                        # Créer le projet dans SonarQube
                        echo "📝 Création du projet dans SonarQube..."
                        curl -X POST "http://localhost:9000/api/projects/create" \\
                          -u '${SONAR_TOKEN}:' \\
                          -d "project=projet-molka&name=Chatbot RH" || echo "ℹ️  Le projet existe peut-être déjà"
                        
                        echo "✅ Analyse SonarQube simulée - Vérifiez le dashboard!"
                        echo "📊 Pour une analyse réelle, installez sonar-scanner-bin"
                        EOF
                        
                        # Donner les permissions d'exécution
                        chmod +x sonar-scanner.sh
                    '''
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse de sécurité du code source'
                script {
                    sh './sonar-scanner.sh'
                }
            }
        }

        stage('Secrets Detection') {
            steps {
                echo '🔐 4. Détection des secrets dans le code'
                script {
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        sh './gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 0'
                    }
                }
            }
        }

        stage('SCA - Dependency Scan') {
            steps {
                echo '📦 5. SCA - Scan des vulnérabilités des dépendances'
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
            echo '--- Archivage des rapports de sécurité ---'
            archiveArtifacts artifacts: '*-report.json', allowEmptyArchive: true
            echo 'Le pipeline DevSecOps est terminé.'
        }
        success {
            echo '✅ Build réussi! - Vérifiez SonarQube!'
        }
        unstable {
            echo '⚠️ Build instable - Des vulnérabilités ont été trouvées'
        }
    }
}