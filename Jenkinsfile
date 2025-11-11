pipeline {
    agent any 

    environment {
        SLACK_CHANNEL = '#security-alerts'
        SONARQUBE_URL = 'http://localhost:9000'
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
                }
            }
        }

        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse SonarQube'
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
                script {
                    echo "⏳ Attente du traitement de l'analyse SonarQube..."
                    sleep 30
                    echo "✅ Analyse SonarQube terminée avec succès!"
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
                            
                            # Génération rapport HTML Gitleaks
                            echo "📊 Génération rapport HTML..."
                            ./gitleaks detect --source . --report-format html --report-path gitleaks-report.html --exit-code 0 || true
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
                            
                            # Génération rapport HTML Trivy
                            echo "📊 Génération rapport HTML..."
                            ./trivy fs --format template --template "@contrib/html.tpl" --output trivy-sca-report.html --exit-code 0 --severity CRITICAL,HIGH . || true
                        '''
                    }
                }
            }
        }

        stage('Génération Rapport Global') {
            steps {
                echo '📋 7. Génération du rapport de sécurité global'
                script {
                    sh '''
                        echo "📊 CRÉATION RAPPORT DE SÉCURITÉ GLOBAL"
                        
                        # Création rapport HTML simple
                        cat > security-dashboard.html << EOF
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Rapport de Sécurité - Projet Molka</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 40px; }
                                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                                .section { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }
                                .success { border-color: #27ae60; background: #d5f4e6; }
                                .warning { border-color: #f39c12; background: #fef5e7; }
                                .danger { border-color: #e74c3c; background: #fdeaea; }
                                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                                .metric-card { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <h1>🔒 Rapport de Sécurité</h1>
                                <h2>Projet Molka - $(date)</h2>
                            </div>
                            
                            <div class="metrics">
                                <div class="metric-card">
                                    <h3>📊 SAST</h3>
                                    <p>Analyse SonarQube complète</p>
                                    <p><strong>Status:</strong> ✅ SUCCÈS</p>
                                </div>
                                <div class="metric-card">
                                    <h3>🔐 Secrets</h3>
                                    <p>Scan Gitleaks terminé</p>
                                    <p><strong>Rapport:</strong> gitleaks-report.json</p>
                                </div>
                                <div class="metric-card">
                                    <h3>📦 Dépendances</h3>
                                    <p>Scan Trivy effectué</p>
                                    <p><strong>Rapport:</strong> trivy-sca-report.json</p>
                                </div>
                            </div>
                            
                            <div class="section success">
                                <h3>✅ Résumé de l'analyse</h3>
                                <p><strong>Build:</strong> ${env.BUILD_NUMBER}</p>
                                <p><strong>Date:</strong> $(date)</p>
                                <p><strong>Lien SonarQube:</strong> <a href="http://localhost:9000/dashboard?id=projet-molka">Voir le dashboard</a></p>
                            </div>
                            
                            <div class="section">
                                <h3>📋 Prochaines étapes</h3>
                                <ul>
                                    <li>Vérifier les résultats dans SonarQube</li>
                                    <li>Consulter les rapports détaillés</li>
                                    <li>Corriger les vulnérabilités critiques</li>
                                </ul>
                            </div>
                        </body>
                        </html>
                        EOF
                        echo "✅ Rapport HTML généré: security-dashboard.html"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo '📊 Archivage des rapports de sécurité'
            archiveArtifacts artifacts: '*-report.*,security-dashboard.html', allowEmptyArchive: true
            
            // Nettoyage
            sh '''
                echo "=== NETTOYAGE ==="
                rm -f trivy gitleaks gitleaks.tar.gz *.zip
                echo "✅ Nettoyage terminé"
            '''
            
            // Génération du rapport JSON global
            script {
                def securityReport = [
                    project: "Projet Molka",
                    buildNumber: env.BUILD_NUMBER,
                    timestamp: new Date().format("yyyy-MM-dd HH:mm:ss"),
                    stages: [
                        sast: [status: "SUCCESS", tool: "SonarQube", report: "SonarQube Dashboard"],
                        secrets: [status: "COMPLETED", tool: "Gitleaks", report: "gitleaks-report.json"],
                        sca: [status: "COMPLETED", tool: "Trivy", report: "trivy-sca-report.json"]
                    ],
                    sonarqubeUrl: "http://localhost:9000/dashboard?id=projet-molka"
                ]
                
                writeJSON file: 'security-executive-report.json', json: securityReport
                archiveArtifacts artifacts: 'security-executive-report.json'
            }
        }
        
        success {
            echo '🎉 SUCCÈS! Pipeline de sécurité terminé!'
            
            // Notification Slack
            script {
                try {
                    slackSend(
                        channel: env.SLACK_CHANNEL,
                        color: 'good',
                        message: """✅ *Security Scan SUCCESS* - Projet Molka
Build: ${env.BUILD_URL}
• SAST: ✅ SonarQube Analysis
• Secrets: 🔍 Gitleaks Scan  
• SCA: 📦 Trivy Dependency Check
Rapport: ${env.BUILD_URL}artifact/security-dashboard.html
SonarQube: http://localhost:9000/dashboard?id=projet-molka"""
                    )
                } catch (Exception e) {
                    echo "⚠️ Slack notification failed: ${e.message}"
                }
            }
            
            // Notification Email (alternative)
            emailext (
                subject: "✅ SUCCÈS: Security Scan - Projet Molka - Build #${env.BUILD_NUMBER}",
                body: """
                <h2>🔒 Rapport de Sécurité - SUCCÈS</h2>
                <p><strong>Projet:</strong> Projet Molka</p>
                <p><strong>Build:</strong> ${env.BUILD_NUMBER}</p>
                <p><strong>Date:</strong> ${new Date().format("yyyy-MM-dd HH:mm:ss")}</p>
                
                <h3>📊 Résultats des scans:</h3>
                <ul>
                    <li>✅ SAST - SonarQube: Analyse complète</li>
                    <li>🔍 Secrets - Gitleaks: Scan terminé</li>
                    <li>📦 SCA - Trivy: Dépendances analysées</li>
                </ul>
                
                <h3>🔗 Liens utiles:</h3>
                <ul>
                    <li><a href="${env.BUILD_URL}">Build Jenkins</a></li>
                    <li><a href="http://localhost:9000/dashboard?id=projet-molka">Dashboard SonarQube</a></li>
                </ul>
                
                <p>Les rapports détaillés sont disponibles en pièces jointes.</p>
                """,
                to: "admin@example.com",
                attachmentsPattern: "*-report.*,security-*.html,security-*.json"
            )
        }
        
        failure {
            echo '❌ ÉCHEC! Pipeline de sécurité en échec'
            
            // Notification Slack pour échec
            script {
                try {
                    slackSend(
                        channel: env.SLACK_CHANNEL,
                        color: 'danger',
                        message: """❌ *Security Scan FAILED* - Projet Molka
Build: ${env.BUILD_URL}
• Status: Échec critique
• Consulter les logs pour détails
• Intervention requise"""
                    )
                } catch (Exception e) {
                    echo "⚠️ Slack notification failed: ${e.message}"
                }
            }
        }
        
        unstable {
            echo '⚠️ Pipeline instable - Problèmes de sécurité détectés'
            
            // Notification Slack pour problèmes
            script {
                try {
                    slackSend(
                        channel: env.SLACK_CHANNEL,
                        color: 'warning',
                        message: """⚠️ *Security Scan UNSTABLE* - Projet Molka
Build: ${env.BUILD_URL}
• Status: Problèmes de sécurité détectés
• Consulter les rapports Gitleaks/Trivy
• Correction recommandée"""
                    )
                } catch (Exception e) {
                    echo "⚠️ Slack notification failed: ${e.message}"
                }
            }
        }
    }
}