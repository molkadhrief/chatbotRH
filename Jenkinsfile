pipeline {
    agent any 
    
    environment {
        SONARQUBE_URL = 'http://localhost:9000'
        BUILD_START_TIME = sh(script: 'date +%s', returnStdout: true).trim()
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
                echo '🛠️ 2. Installation outils DevSecOps'
                script {
                    sh '''
                        # Installation Trivy
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest
                        ./trivy --version
                        
                        # Installation Gitleaks
                        curl -L -o gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.29.0/gitleaks_8.29.0_linux_x64.tar.gz
                        tar -xzf gitleaks.tar.gz
                        chmod +x gitleaks
                        ./gitleaks version
                        
                        echo "✅ Outils DevSecOps installés"
                    '''
                }
            }
        }
        
        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse statique du code'
                withSonarQubeEnv('sonar-server') {
                    script {
                        withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                            sh '''
                                echo "🚀 Lancement analyse SonarQube..."
                                sonar-scanner \
                                -Dsonar.projectKey=projet-molka \
                                -Dsonar.sources=. \
                                -Dsonar.projectName="Projet Molka DevSecOps" \
                                -Dsonar.host.url=http://localhost:9000 \
                                -Dsonar.token=${SONAR_TOKEN} \
                                -Dsonar.sourceEncoding=UTF-8
                                echo "✅ Analyse SonarQube terminée"
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Security Scans') {
            parallel {
                stage('Secrets Detection') {
                    steps {
                        echo '🔐 4. Détection des secrets - Gitleaks'
                        script {
                            sh '''
                                echo "=== DÉTECTION DES SECRETS ==="
                                ./gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 0
                                
                                SECRETS_COUNT=$(jq '. | length' gitleaks-report.json 2>/dev/null || echo "0")
                                echo "SECRETS_COUNT=${SECRETS_COUNT}" > security-metrics.txt
                                
                                if [ "$SECRETS_COUNT" -gt 0 ]; then
                                    echo "⚠️  ATTENTION: $SECRETS_COUNT secret(s) potentiel(s) détecté(s)"
                                else
                                    echo "✅ Aucun secret détecté"
                                fi
                                echo "✅ Scan Gitleaks terminé"
                            '''
                        }
                    }
                }
                
                stage('SCA - Trivy Scan') {
                    steps {
                        echo '📦 5. SCA - Scan des dépendances (Trivy)'
                        script {
                            sh '''
                                echo "=== SCAN TRIVY ==="
                                ./trivy fs --format json --output trivy-sca-report.json --exit-code 0 --severity CRITICAL,HIGH .
                                
                                CRITICAL_COUNT=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | .VulnerabilityID' trivy-sca-report.json 2>/dev/null | wc -l || echo "0")
                                HIGH_COUNT=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH") | .VulnerabilityID' trivy-sca-report.json 2>/dev/null | wc -l || echo "0")
                                
                                echo "VULN_CRITICAL=${CRITICAL_COUNT}" >> security-metrics.txt
                                echo "VULN_HIGH=${HIGH_COUNT}" >> security-metrics.txt
                                
                                if [ "$CRITICAL_COUNT" -gt 0 ] || [ "$HIGH_COUNT" -gt 0 ]; then
                                    echo "⚠️  VULNÉRABILITÉS DÉTECTÉES: CRITICAL=$CRITICAL_COUNT, HIGH=$HIGH_COUNT"
                                else
                                    echo "✅ Aucune vulnérabilité CRITICAL/HIGH détectée"
                                fi
                                echo "✅ Scan Trivy terminé"
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Generate Prometheus Metrics') {
            steps {
                echo '📊 6. Génération métriques Prometheus'
                script {
                    sh '''
                        # Lire les métriques de sécurité
                        if [ -f security-metrics.txt ]; then
                            source security-metrics.txt
                        else
                            SECRETS_COUNT=0
                            VULN_CRITICAL=0
                            VULN_HIGH=0
                        fi
                        
                        # Calculer la durée du build
                        BUILD_END_TIME=$(date +%s)
                        BUILD_DURATION=$((BUILD_END_TIME - ${BUILD_START_TIME}))
                        
                        # Générer les métriques Prometheus au format texte
                        cat > prometheus-metrics.txt << EOM
                        # HELP devsecops_secrets_detected_total Number of secrets detected in DevSecOps pipeline
                        # TYPE devsecops_secrets_detected_total gauge
                        devsecops_secrets_detected_total{project="projet-molka", environment="dev"} ${SECRETS_COUNT}
                        
                        # HELP devsecops_vulnerabilities_critical_total Number of critical vulnerabilities detected
                        # TYPE devsecops_vulnerabilities_critical_total gauge
                        devsecops_vulnerabilities_critical_total{project="projet-molka", environment="dev"} ${VULN_CRITICAL}
                        
                        # HELP devsecops_vulnerabilities_high_total Number of high vulnerabilities detected
                        # TYPE devsecops_vulnerabilities_high_total gauge
                        devsecops_vulnerabilities_high_total{project="projet-molka", environment="dev"} ${VULN_HIGH}
                        
                        # HELP devsecops_build_duration_seconds DevSecOps pipeline build duration
                        # TYPE devsecops_build_duration_seconds gauge
                        devsecops_build_duration_seconds{project="projet-molka", environment="dev"} ${BUILD_DURATION}
                        
                        # HELP devsecops_scan_success_status DevSecOps scan success status
                        # TYPE devsecops_scan_success_status gauge
                        devsecops_scan_success_status{project="projet-molka", environment="dev"} 1
                        EOM
                        
                        echo "✅ Métriques Prometheus générées :"
                        echo "=== MÉTRIQUES DEVSECOPS ==="
                        cat prometheus-metrics.txt
                    '''
                }
            }
        }
        
        stage('Generate Security Report') {
            steps {
                echo '📋 7. Génération rapport de sécurité'
                script {
                    sh '''
                        # Lire les métriques
                        source security-metrics.txt
                        BUILD_END_TIME=$(date +%s)
                        BUILD_DURATION=$((BUILD_END_TIME - ${BUILD_START_TIME}))
                        
                        # Générer le rapport HTML
                        cat > devsecops-dashboard.html << EOF
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Dashboard DevSecOps - Métriques Prometheus</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 40px; }
                                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
                                .metric-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
                                .metric-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
                                .success { border-left: 5px solid #27ae60; }
                                .warning { border-left: 5px solid #f39c12; }
                                .critical { border-left: 5px solid #e74c3c; }
                                .info { border-left: 5px solid #3498db; }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <h1>📊 Dashboard DevSecOps avec Prometheus</h1>
                                <h2>Projet Molka - Build #${BUILD_NUMBER}</h2>
                                <p>Métriques exportées vers Prometheus pour monitoring temps réel</p>
                            </div>
                            
                            <div class="metrics">
                                <div class="metric-card \$([ $SECRETS_COUNT -gt 0 ] && echo "warning" || echo "success")">
                                    <h3>🔐 Secrets Détectés</h3>
                                    <div class="metric-value">$SECRETS_COUNT</div>
                                    <p>Métrique: devsecops_secrets_detected_total</p>
                                </div>
                                
                                <div class="metric-card \$([ $VULN_CRITICAL -gt 0 ] && echo "critical" || echo "success")">
                                    <h3>🚨 Vulnérabilités CRITICAL</h3>
                                    <div class="metric-value">$VULN_CRITICAL</div>
                                    <p>Métrique: devsecops_vulnerabilities_critical_total</p>
                                </div>
                                
                                <div class="metric-card \$([ $VULN_HIGH -gt 0 ] && echo "warning" || echo "success")">
                                    <h3>⚠️ Vulnérabilités HIGH</h3>
                                    <div class="metric-value">$VULN_HIGH</div>
                                    <p>Métrique: devsecops_vulnerabilities_high_total</p>
                                </div>
                                
                                <div class="metric-card info">
                                    <h3>⏱️ Durée du Build</h3>
                                    <div class="metric-value">${BUILD_DURATION}s</div>
                                    <p>Métrique: devsecops_build_duration_seconds</p>
                                </div>
                            </div>
                            
                            <div class="metric-card info">
                                <h3>📈 Intégration Prometheus</h3>
                                <p><strong>Métriques générées :</strong></p>
                                <ul>
                                    <li><code>devsecops_secrets_detected_total</code> - Secrets détectés</li>
                                    <li><code>devsecops_vulnerabilities_critical_total</code> - Vulnérabilités CRITICAL</li>
                                    <li><code>devsecops_vulnerabilities_high_total</code> - Vulnérabilités HIGH</li>
                                    <li><code>devsecops_build_duration_seconds</code> - Durée du pipeline</li>
                                    <li><code>devsecops_scan_success_status</code> - Statut des scans</li>
                                </ul>
                                <p><strong>Accès Prometheus :</strong> http://localhost:9090</p>
                                <p><strong>Accès Grafana :</strong> http://localhost:3000</p>
                            </div>
                        </body>
                        </html>
                        EOF
                        
                        echo "✅ Rapport HTML généré avec métriques Prometheus"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '📦 Archivage des rapports et métriques'
            archiveArtifacts artifacts: '*-report.*,security-metrics.txt,prometheus-metrics.txt,devsecops-dashboard.html', allowEmptyArchive: true
            
            // Nettoyage
            sh '''
                echo "=== NETTOYAGE ==="
                rm -f trivy gitleaks gitleaks.tar.gz
                echo "✅ Nettoyage terminé"
            '''
            
            script {
                def secretsCount = sh(script: 'cat security-metrics.txt 2>/dev/null | grep SECRETS_COUNT | cut -d= -f2', returnStdout: true).trim() ?: "0"
                def criticalCount = sh(script: 'cat security-metrics.txt 2>/dev/null | grep VULN_CRITICAL | cut -d= -f2', returnStdout: true).trim() ?: "0"
                def highCount = sh(script: 'cat security-metrics.txt 2>/dev/null | grep VULN_HIGH | cut -d= -f2', returnStdout: true).trim() ?: "0"
                
                echo """
                🎉 PIPELINE DEVSECOPS AVEC PROMETHEUS - TERMINÉ !
                
                📊 MÉTRIQUES GÉNÉRÉES :
                • 🔐 Secrets détectés: ${secretsCount}
                • 🚨 Vulnérabilités CRITICAL: ${criticalCount}
                • ⚠️  Vulnérabilités HIGH: ${highCount}
                
                📈 INTÉGRATION PROMETHEUS :
                • Métriques exportées: prometheus-metrics.txt
                • Dashboard: devsecops-dashboard.html
                • Endpoint: http://localhost:8080/prometheus
                
                🔗 PROCHAINES ÉTAPES :
                1. Redémarrer Jenkins pour activer Prometheus
                2. Tester: curl http://localhost:8080/prometheus
                3. Déployer Grafana pour visualisation
                """
            }
        }
        
        success {
            echo '✅ SUCCÈS! Pipeline DevSecOps + Prometheus COMPLET!'
        }
    }
}