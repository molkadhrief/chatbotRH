pipeline {
    agent any 
    
    environment {
        SONARQUBE_URL = 'http://localhost:9000'
    }
    
    stages {
        stage('Checkout & Real-time Scan Prep') {
            steps { 
                echo '🔍 1. Checkout et préparation scan temps réel'
                checkout scm 
                
                script {
                    // Installation outils scan temps réel
                    sh '''
                        echo "=== INSTALLATION OUTILS TEMPS RÉEL ==="
                        
                        # Installation Semgrep pour scan avancé
                        python -m pip install semgrep
                        
                        # Installation Bandit pour Python
                        pip install bandit
                        
                        # Installation Gitleaks
                        curl -L -o gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.29.0/gitleaks_8.29.0_linux_x64.tar.gz
                        tar -xzf gitleaks.tar.gz
                        chmod +x gitleaks
                        
                        echo "✅ Outils scan temps réel installés"
                    '''
                }
            }
        }
        
        stage('Real-time Security Scan') {
            steps {
                echo '🛡️ 2. Scan de sécurité temps réel'
                script {
                    sh '''
                        echo "=== SCAN SÉCURITÉ TEMPS RÉEL ==="
                        
                        # 1. SCAN SEMGREP - Détection patterns de vulnérabilités
                        echo "🔍 Semgrep - Scan patterns de vulnérabilités..."
                        semgrep --config=auto --json --output semgrep-report.json . || true
                        
                        # Analyse résultats Semgrep
                        if [ -f semgrep-report.json ]; then
                            SEMGREP_ISSUES=$(jq '.results | length' semgrep-report.json 2>/dev/null || echo "0")
                            echo "📊 Semgrep: $SEMGREP_ISSUES problèmes détectés"
                            
                            # Afficher les problèmes critiques
                            jq -r '.results[] | select(.extra.severity == "ERROR") | "❌ \(.extra.message) - \(.path):\(.start.line)"' semgrep-report.json 2>/dev/null || echo "✅ Aucun problème ERROR Semgrep"
                        fi
                        
                        # 2. SCAN BANDIT - Sécurité Python
                        echo "🐍 Bandit - Analyse sécurité Python..."
                        if find . -name "*.py" | grep -q .; then
                            bandit -r . -f json -o bandit-report.json || true
                            
                            if [ -f bandit-report.json ]; then
                                BANDIT_HIGH=$(jq '.metrics._totals.HIGH' bandit-report.json 2>/dev/null || echo "0")
                                BANDIT_MEDIUM=$(jq '.metrics._totals.MEDIUM' bandit-report.json 2>/dev/null || echo "0")
                                echo "📊 Bandit: HIGH=$BANDIT_HIGH, MEDIUM=$BANDIT_MEDIUM"
                                
                                # Afficher les vulnérabilités HIGH
                                jq -r '.results[] | select(.issue_severity == "HIGH") | "🚨 \(.issue_text) - \(.filename):\(.line_number)"' bandit-report.json 2>/dev/null | head -5 || echo "✅ Aucune vulnérabilité HIGH Bandit"
                            fi
                        else
                            echo "ℹ️  Aucun fichier Python à analyser avec Bandit"
                        fi
                        
                        # 3. SCAN TEMPS RÉEL AVEC GITLEAKS
                        echo "🔐 Gitleaks - Scan secrets temps réel..."
                        ./gitleaks detect --source . --report-format json --report-path gitleaks-realtime-report.json --exit-code 0 --verbose
                        
                        SECRETS_COUNT=$(jq '. | length' gitleaks-realtime-report.json 2>/dev/null || echo "0")
                        echo "📊 Gitleaks: $SECRETS_COUNT secrets potentiels"
                        
                        # Afficher les secrets détectés
                        if [ "$SECRETS_COUNT" -gt 0 ]; then
                            jq -r '.[] | "🔐 \(.Description) - \(.File):\(.StartLine)"' gitleaks-realtime-report.json 2>/dev/null
                        fi
                        
                        # 4. SCAN DE VULNÉRABILITÉS CONNUES
                        echo "📝 Scan vulnérabilités connues..."
                        
                        # Scan XSS potentiel
                        if find . -name "*.html" -o -name "*.js" | xargs grep -l "innerHTML\\|eval(" 2>/dev/null; then
                            echo "⚠️  XSS Potentiel: innerHTML ou eval() détecté"
                        fi
                        
                        # Scan injections SQL
                        if find . -name "*.py" -o -name "*.php" | xargs grep -l "sqlite3\\|mysql.*connect" 2>/dev/null; then
                            echo "⚠️  Injection SQL Potentielle: Connexion DB directe détectée"
                        fi
                        
                        echo "✅ Scan temps réel terminé"
                    '''
                }
            }
        }
        
        stage('SAST - SonarQube Deep Analysis') {
            steps {
                echo '🔎 3. SAST - Analyse approfondie SonarQube'
                withSonarQubeEnv('sonar-server') {
                    script {
                        withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                            sh '''
                                echo "🚀 Lancement analyse SonarQube approfondie..."
                                sonar-scanner \
                                -Dsonar.projectKey=projet-molka \
                                -Dsonar.sources=. \
                                -Dsonar.projectName="Projet Molka DevSecOps" \
                                -Dsonar.host.url=http://localhost:9000 \
                                -Dsonar.token=${SONAR_TOKEN} \
                                -Dsonar.python.version=3.8 \
                                -Dsonar.sourceEncoding=UTF-8
                                echo "✅ Analyse SonarQube terminée"
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Real-time Security Dashboard') {
            steps {
                echo '📊 4. Dashboard temps réel des vulnérabilités'
                script {
                    sh '''
                        echo "=== DASHBOARD TEMPS RÉEL ==="
                        
                        # Collecte des métriques
                        SECRETS_COUNT=$(jq '. | length' gitleaks-realtime-report.json 2>/dev/null || echo "0")
                        SEMGREP_ISSUES=$(jq '.results | length' semgrep-report.json 2>/dev/null || echo "0")
                        BANDIT_HIGH=$(jq '.metrics._totals.HIGH' bandit-report.json 2>/dev/null || echo "0")
                        BANDIT_MEDIUM=$(jq '.metrics._totals.MEDIUM' bandit-report.json 2>/dev/null || echo "0")
                        
                        # Génération dashboard temps réel
                        cat > realtime-security-dashboard.html << EOF
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Dashboard Sécurité Temps Réel</title>
                            <style>
                                body { font-family: Arial, sans-serif; margin: 40px; }
                                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                                .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                                .metric-card { background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
                                .critical { border-left: 5px solid #e74c3c; }
                                .warning { border-left: 5px solid #f39c12; }
                                .info { border-left: 5px solid #3498db; }
                                .live-indicator { animation: pulse 2s infinite; }
                                @keyframes pulse {
                                    0% { opacity: 1; }
                                    50% { opacity: 0.5; }
                                    100% { opacity: 1; }
                                }
                            </style>
                        </head>
                        <body>
                            <div class="header">
                                <h1>🛡️ Dashboard Sécurité Temps Réel</h1>
                                <h2>Projet Molka - Scan Live</h2>
                                <p>🟢 <span class="live-indicator">SCAN EN TEMPS RÉEL</span> - Dernière mise à jour: $(date)</p>
                            </div>
                            
                            <div class="metrics">
                                <div class="metric-card \$([ $SECRETS_COUNT -gt 0 ] && echo "critical" || echo "info")">
                                    <h3>🔐 Secrets</h3>
                                    <div style="font-size: 2.5em; font-weight: bold;">$SECRETS_COUNT</div>
                                    <p>Secrets exposés détectés</p>
                                </div>
                                
                                <div class="metric-card \$([ $SEMGREP_ISSUES -gt 0 ] && echo "warning" || echo "info")">
                                    <h3>📝 Patterns Risque</h3>
                                    <div style="font-size: 2.5em; font-weight: bold;">$SEMGREP_ISSUES</div>
                                    <p>Patterns de vulnérabilités</p>
                                </div>
                                
                                <div class="metric-card \$([ $BANDIT_HIGH -gt 0 ] && echo "critical" || echo "info")">
                                    <h3>🐍 Python HIGH</h3>
                                    <div style="font-size: 2.5em; font-weight: bold;">$BANDIT_HIGH</div>
                                    <p>Vulnérabilités Python</p>
                                </div>
                                
                                <div class="metric-card \$([ $BANDIT_MEDIUM -gt 0 ] && echo "warning" || echo "info")">
                                    <h3>🐍 Python MEDIUM</h3>
                                    <div style="font-size: 2.5em; font-weight: bold;">$BANDIT_MEDIUM</div>
                                    <p>Vulnérabilités Python</p>
                                </div>
                            </div>
                            
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                                <h3>🔍 Détections Temps Réel Actives</h3>
                                <ul>
                                    <li>✅ <strong>Semgrep:</strong> Scan patterns vulnérabilités (XSS, Injection, etc.)</li>
                                    <li>✅ <strong>Bandit:</strong> Analyse sécurité Python spécifique</li>
                                    <li>✅ <strong>Gitleaks:</strong> Détection secrets et credentials</li>
                                    <li>✅ <strong>SonarQube:</strong> Analyse statique approfondie</li>
                                    <li>✅ <strong>Custom Rules:</strong> Scan vulnérabilités métier</li>
                                </ul>
                            </div>
                            
                            <div style="background: #e8f4fd; padding: 15px; border-radius: 5px;">
                                <h3>🚨 Alertes Temps Réel</h3>
                                <div id="live-alerts">
                                    <p>Scan en cours... Détections live</p>
                                </div>
                            </div>
                        </body>
                        </html>
                        EOF
                        
                        echo "✅ Dashboard temps réel généré"
                    '''
                }
            }
        }
        
        stage('Blocking Security Gate') {
            steps {
                echo '🚨 5. Porte de sécurité bloquante'
                script {
                    sh '''
                        echo "=== VÉRIFICATION BLOQUANTE ==="
                        
                        SECRETS_COUNT=$(jq '. | length' gitleaks-realtime-report.json 2>/dev/null || echo "0")
                        BANDIT_HIGH=$(jq '.metrics._totals.HIGH' bandit-report.json 2>/dev/null || echo "0")
                        
                        # Règles de blocage STRICTES
                        if [ "$SECRETS_COUNT" -gt 0 ]; then
                            echo "❌ BLOQUÉ: $SECRETS_COUNT secret(s) détecté(s) - Correction requise!"
                            echo "🔍 Détails:"
                            jq -r '.[] | "   - \(.Description) dans \(.File):\(.StartLine)"' gitleaks-realtime-report.json 2>/dev/null
                            currentBuild.result = 'FAILURE'
                            error "Build bloqué par sécurité"
                        fi
                        
                        if [ "$BANDIT_HIGH" -gt 2 ]; then
                            echo "❌ BLOQUÉ: $BANDIT_HIGH vulnérabilités HIGH Python - Correction requise!"
                            currentBuild.result = 'FAILURE'
                            error "Build bloqué par sécurité"
                        fi
                        
                        echo "✅ Porte de sécurité passée - Aucun blocage critique"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '📊 Archivage rapports temps réel'
            archiveArtifacts artifacts: '*-report.*,realtime-security-dashboard.html,bandit-report.json,semgrep-report.json', allowEmptyArchive: true
            
            // Nettoyage
            sh '''
                rm -f gitleaks gitleaks.tar.gz
                echo "✅ Nettoyage terminé"
            '''
            
            script {
                echo """
                🎉 SCAN TEMPS RÉEL TERMINÉ!
                
                📊 OUTILS TEMPS RÉEL UTILISÉS:
                • 🔍 Semgrep: Scan patterns vulnérabilités
                • 🐍 Bandit: Analyse sécurité Python  
                • 🔐 Gitleaks: Détection secrets
                • 📝 Custom Rules: Vulnérabilités métier
                
                📁 RAPPORTS GÉNÉRÉS:
                • realtime-security-dashboard.html
                • semgrep-report.json
                • bandit-report.json
                • gitleaks-realtime-report.json
                """
            }
        }
    }
}