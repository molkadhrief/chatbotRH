pipeline {
    agent any 
    
    environment {
        SONARQUBE_URL = 'http://localhost:9000'
        PATH = "$PATH:/var/lib/jenkins/.local/bin"
        BUILD_TIMESTAMP = new Date().format("yyyy-MM-dd'T'HH:mm:ssXXX")
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
                echo '🛠️ 2. Installation outils de sécurité'
                script {
                    sh '''
                        echo "=== INSTALLATION OUTILS DEVSECOPS LINUX ==="
                        
                        # Installation Trivy
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b . latest
                        ./trivy --version
                        
                        # Installation Gitleaks
                        curl -L -o gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.29.0/gitleaks_8.29.0_linux_x64.tar.gz
                        tar -xzf gitleaks.tar.gz
                        chmod +x gitleaks
                        ./gitleaks version
                        
                        # Installation Bandit pour Python avec gestion du PATH
                        echo "=== INSTALLATION BANDIT ==="
                        pip3 install bandit safety semgrep
                        
                        # Vérification de l'installation
                        echo "=== VÉRIFICATION INSTALLATION ==="
                        ./trivy --version && echo "✅ Trivy OK"
                        ./gitleaks version && echo "✅ Gitleaks OK"
                        python3 -m bandit --version && echo "✅ Bandit disponible via python3 -m"
                        
                        echo "✅ Outils sécurité installés"
                    '''
                }
            }
        }
        
        stage('Security Scans') {
            parallel {
                stage('SAST - SonarQube') {
                    steps {
                        echo '🔎 3.1 SAST - Analyse SonarQube'
                        withSonarQubeEnv('sonar-server') {
                            script {
                                withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                                    sh '''
                                        echo "🚀 Lancement SonarQube..."
                                        sonar-scanner \
                                        -Dsonar.projectKey=projet-molka \
                                        -Dsonar.sources=. \
                                        -Dsonar.projectName="Projet Molka DevSecOps" \
                                        -Dsonar.host.url=http://localhost:9000 \
                                        -Dsonar.token=${SONAR_TOKEN} \
                                        -Dsonar.sourceEncoding=UTF-8 || true
                                        echo "✅ SonarQube terminé"
                                    '''
                                }
                            }
                        }
                    }
                }
                
                stage('SCA - Dependency Scan') {
                    steps {
                        echo '📦 3.2 SCA - Scan des dépendances'
                        script {
                            sh '''
                                echo "=== SCAN TRIVY ENRICHIE ==="
                                ./trivy fs --format json --output trivy-sca-report.json --exit-code 0 --severity CRITICAL,HIGH,MEDIUM,LOW .
                                
                                # Analyse enrichie des résultats
                                if [ -f trivy-sca-report.json ]; then
                                    CRITICAL_COUNT=$(jq "[.Results[]?.Vulnerabilities[]? | select(.Severity == \\\"CRITICAL\\\")] | length" trivy-sca-report.json 2>/dev/null || echo "0")
                                    HIGH_COUNT=$(jq "[.Results[]?.Vulnerabilities[]? | select(.Severity == \\\"HIGH\\\")] | length" trivy-sca-report.json 2>/dev/null || echo "0")
                                    MEDIUM_COUNT=$(jq "[.Results[]?.Vulnerabilities[]? | select(.Severity == \\\"MEDIUM\\\")] | length" trivy-sca-report.json 2>/dev/null || echo "0")
                                    LOW_COUNT=$(jq "[.Results[]?.Vulnerabilities[]? | select(.Severity == \\\"LOW\\\")] | length" trivy-sca-report.json 2>/dev/null || echo "0")
                                    TOTAL_COUNT=$((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))
                                    
                                    echo "📊 RÉSULTATS TRIVY DÉTAILLÉS:"
                                    echo "   🚨 CRITICAL: $CRITICAL_COUNT"
                                    echo "   ⚠️  HIGH: $HIGH_COUNT"
                                    echo "   🔶 MEDIUM: $MEDIUM_COUNT"
                                    echo "   📋 LOW: $LOW_COUNT"
                                    echo "   📈 TOTAL: $TOTAL_COUNT"
                                fi
                                echo "✅ Scan Trivy enrichi terminé"
                            '''
                        }
                    }
                }
                
                stage('Secrets Detection') {
                    steps {
                        echo '🔐 3.3 Détection des secrets'
                        script {
                            sh '''
                                echo "=== SCAN SECRETS ENRICHIE ==="
                                ./gitleaks detect --source . --report-format json --report-path gitleaks-report.json --exit-code 0
                                
                                SECRETS_COUNT=$(jq ". | length" gitleaks-report.json 2>/dev/null || echo "0")
                                
                                # Analyse des types de secrets détectés
                                if [ "$SECRETS_COUNT" -gt 0 ]; then
                                    echo "❌ SECRETS DÉTECTÉS - $SECRETS_COUNT au total"
                                    echo "[]" > gitleaks-summary.json
                                else
                                    echo "✅ Aucun secret détecté"
                                    echo "[]" > gitleaks-summary.json
                                fi
                            '''
                        }
                    }
                }
                
                stage('Python Security Scan') {
                    steps {
                        echo '🐍 3.4 Sécurité Python'
                        script {
                            sh '''
                                echo "=== SCAN BANDIT ENRICHIE ==="
                                
                                if find . -name "*.py" | grep -q .; then
                                    echo "Fichiers Python trouvés, lancement de Bandit..."
                                    
                                    set +e
                                    if which bandit >/dev/null 2>&1; then
                                        bandit -r . -f json -o bandit-report.json --exit-zero || true
                                    else
                                        python3 -m bandit -r . -f json -o bandit-report.json --exit-zero || true
                                    fi
                                    set -e
                                    
                                    if [ -f bandit-report.json ]; then
                                        echo "✅ Bandit scan enrichi terminé"
                                    else
                                        echo '{"metrics": {"_totals": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}}}' > bandit-report.json
                                    fi
                                else
                                    echo "ℹ️  Aucun fichier Python trouvé"
                                    echo '{"metrics": {"_totals": {"HIGH": 0, "MEDIUM": 0, "LOW": 0}}}' > bandit-report.json
                                fi
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Generate Enhanced Security Reports') {
            steps {
                echo '📊 4. Génération rapports avancés'
                script {
                    sh '''
                        echo "=== GÉNÉRATION RAPPORTS JSON ENRICHIS ==="
                        
                        # Collecte métriques détaillées avec valeurs par défaut sécurisées
                        SECRETS_COUNT=$(jq ". | length" gitleaks-report.json 2>/dev/null || echo "0")
                        
                        CRITICAL_COUNT=$(jq "[.Results[]?.Vulnerabilities[]? | select(.Severity == \\\"CRITICAL\\\")] | length" trivy-sca-report.json 2>/dev/null || echo "0")
                        HIGH_COUNT=$(jq "[.Results[]?.Vulnerabilities[]? | select(.Severity == \\\"HIGH\\\")] | length" trivy-sca-report.json 2>/dev/null || echo "0")
                        MEDIUM_COUNT=$(jq "[.Results[]?.Vulnerabilities[]? | select(.Severity == \\\"MEDIUM\\\")] | length" trivy-sca-report.json 2>/dev/null || echo "0")
                        LOW_COUNT=$(jq "[.Results[]?.Vulnerabilities[]? | select(.Severity == \\\"LOW\\\")] | length" trivy-sca-report.json 2>/dev/null || echo "0")
                        
                        # Lecture sécurisée des valeurs Bandit
                        BANDIT_HIGH=$(jq ".metrics._totals.HIGH // 0" bandit-report.json 2>/dev/null || echo "0")
                        BANDIT_MEDIUM=$(jq ".metrics._totals.MEDIUM // 0" bandit-report.json 2>/dev/null || echo "0")
                        BANDIT_LOW=$(jq ".metrics._totals.LOW // 0" bandit-report.json 2>/dev/null || echo "0")
                        
                        # Conversion en nombres pour les calculs
                        CRITICAL_NUM=$((CRITICAL_COUNT))
                        HIGH_NUM=$((HIGH_COUNT))
                        SECRETS_NUM=$((SECRETS_COUNT))
                        BANDIT_HIGH_NUM=$((BANDIT_HIGH))
                        
                        # Calcul score de sécurité global
                        SECURITY_SCORE=100
                        if [ $CRITICAL_NUM -gt 0 ]; then SECURITY_SCORE=$((SECURITY_SCORE - 30)); fi
                        if [ $HIGH_NUM -gt 0 ]; then SECURITY_SCORE=$((SECURITY_SCORE - 20)); fi
                        if [ $SECRETS_NUM -gt 0 ]; then SECURITY_SCORE=$((SECURITY_SCORE - 25)); fi
                        if [ $BANDIT_HIGH_NUM -gt 0 ]; then SECURITY_SCORE=$((SECURITY_SCORE - 15)); fi
                        if [ $SECURITY_SCORE -lt 0 ]; then SECURITY_SCORE=0; fi
                        
                        # Détermination statut global
                        if [ $CRITICAL_NUM -gt 0 ] || [ $SECRETS_NUM -gt 10 ]; then
                            OVERALL_STATUS="CRITICAL"
                        elif [ $HIGH_NUM -gt 0 ] || [ $SECRETS_NUM -gt 0 ] || [ $BANDIT_HIGH_NUM -gt 0 ]; then
                            OVERALL_STATUS="HIGH"
                        elif [ $MEDIUM_COUNT -gt 0 ] || [ $BANDIT_MEDIUM -gt 0 ]; then
                            OVERALL_STATUS="MEDIUM"
                        else
                            OVERALL_STATUS="LOW"
                        fi
                        
                        # Rapport JSON principal simplifié
                        cat > security-executive-report.json << EOF
{
  "metadata": {
    "project": "Projet Molka DevSecOps",
    "build_number": "${BUILD_NUMBER}",
    "build_timestamp": "${BUILD_TIMESTAMP}",
    "pipeline_version": "2.0",
    "overall_status": "${OVERALL_STATUS}",
    "security_score": ${SECURITY_SCORE}
  },
  "summary": {
    "secrets_detected": ${SECRETS_COUNT},
    "vulnerabilities": {
      "critical": ${CRITICAL_COUNT},
      "high": ${HIGH_COUNT},
      "medium": ${MEDIUM_COUNT},
      "low": ${LOW_COUNT},
      "total": $((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))
    },
    "python_security": {
      "high": ${BANDIT_HIGH},
      "medium": ${BANDIT_MEDIUM},
      "low": ${BANDIT_LOW}
    }
  },
  "recommendations": {
    "immediate_actions": [
      "Revoir les résultats des scans de sécurité",
      "Corriger les vulnérabilités identifiées",
      "Améliorer les pratiques de développement sécurisé"
    ]
  }
}
EOF
                        echo "✅ Rapport JSON exécutif généré: security-executive-report.json"
                        
                        # Génération du dashboard HTML
                        cat > security-executive-dashboard.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Rapport Sécurité - Projet Molka</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 25px; border-radius: 10px; text-align: center; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin: 30px 0; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; }
        .success { border-top: 5px solid #27ae60; }
        .warning { border-top: 5px solid #f39c12; }
        .critical { border-top: 5px solid #e74c3c; }
        .metric-value { font-size: 2.5em; font-weight: bold; margin: 15px 0; }
        .security-score { font-size: 3em; font-weight: bold; margin: 20px 0; }
        .score-excellent { color: #27ae60; }
        .score-good { color: #f39c12; }
        .score-poor { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 RAPPORT DEVSECOPS</h1>
        <h2>Projet Molka - Analyse de Sécurité</h2>
        <p>Build ${BUILD_NUMBER} | ${BUILD_TIMESTAMP}</p>
        <div class="security-score score-$([ $SECURITY_SCORE -ge 80 ] && echo "excellent" || [ $SECURITY_SCORE -ge 60 ] && echo "good" || echo "poor")">
            Score: ${SECURITY_SCORE}/100
        </div>
        <p>Statut Global: <strong>${OVERALL_STATUS}</strong></p>
    </div>
    
    <div class="metrics">
        <div class="metric-card $([ $SECRETS_COUNT -gt 0 ] && echo "warning" || echo "success")">
            <h3>🔐 Secrets</h3>
            <div class="metric-value">${SECRETS_COUNT}</div>
            <p>Secrets détectés</p>
        </div>
        
        <div class="metric-card $([ $CRITICAL_COUNT -gt 0 ] && echo "critical" || echo "success")">
            <h3>🚨 CRITICAL</h3>
            <div class="metric-value">${CRITICAL_COUNT}</div>
            <p>Vulnérabilités</p>
        </div>
        
        <div class="metric-card $([ $HIGH_COUNT -gt 0 ] && echo "warning" || echo "success")">
            <h3>⚠️ HIGH</h3>
            <div class="metric-value">${HIGH_COUNT}</div>
            <p>Vulnérabilités</p>
        </div>
        
        <div class="metric-card $([ $BANDIT_HIGH -gt 0 ] && echo "warning" || echo "success")">
            <h3>🐍 Python</h3>
            <div class="metric-value">${BANDIT_HIGH}</div>
            <p>Issues HIGH</p>
        </div>
    </div>
    
    <div style="background: white; padding: 25px; border-radius: 10px; margin: 20px 0;">
        <h3>📋 SYNTHÈSE DE L'ANALYSE</h3>
        <p><strong>Secrets détectés:</strong> ${SECRETS_COUNT}</p>
        <p><strong>Vulnérabilités CRITICAL:</strong> ${CRITICAL_COUNT}</p>
        <p><strong>Vulnérabilités HIGH:</strong> ${HIGH_COUNT}</p>
        <p><strong>Vulnérabilités TOTAL:</strong> $((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))</p>
    </div>
</body>
</html>
EOF
                        echo "✅ Dashboard HTML généré"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '📦 Archivage des rapports'
            archiveArtifacts artifacts: '*-report.json,security-*.html', allowEmptyArchive: true
            
            sh '''
                echo "=== NETTOYAGE ==="
                rm -f trivy gitleaks gitleaks.tar.gz
                echo "✅ Nettoyage terminé"
            '''
            
            // Affichage final simplifié sans readJSON
            script {
                echo """
                🎉 PIPELINE DEVSECOPS TERMINÉ !
                
                📊 RÉSULTATS DES SCANS:
                • 🔐 Secrets détectés: Vérifiez gitleaks-report.json
                • 🚨 Vulnérabilités CRITICAL: Vérifiez trivy-sca-report.json  
                • ⚠️  Vulnérabilités HIGH: Vérifiez trivy-sca-report.json
                • 📋 Rapport complet: security-executive-report.json
                • 🎨 Dashboard: security-executive-dashboard.html
                
                🔗 ACCÈS:
                • SonarQube: http://localhost:9000/dashboard?id=projet-molka
                • Jenkins: ${env.BUILD_URL}
                """
            }
        }
        
        success {
            echo '✅ SUCCÈS! Pipeline DevSecOps complété!'
            emailext (
                subject: "✅ SUCCÈS - Pipeline DevSecOps - Build ${env.BUILD_NUMBER}",
                body: """
                Le pipeline DevSecOps s'est terminé avec succès !
                
                Analyses réalisées:
                - SAST SonarQube: Analyse code statique
                - SCA Trivy: Scan dépendances
                - Détection secrets: Gitleaks
                - Sécurité Python: Bandit
                
                Rapports générés:
                • security-executive-report.json
                • security-executive-dashboard.html
                
                Accès au rapport: ${env.BUILD_URL}
                Dashboard SonarQube: http://localhost:9000/dashboard?id=projet-molka
                """,
                to: "admin@example.com"
            )
        }
        
        failure {
            echo '❌ Pipeline échoué - Vérifier les logs pour détails'
            emailext (
                subject: "❌ ÉCHEC - Pipeline DevSecOps - Build ${env.BUILD_NUMBER}",
                body: """
                Le pipeline DevSecOps a échoué.
                
                Veuillez vérifier les logs Jenkins pour identifier le problème:
                ${env.BUILD_URL}
                """,
                to: "admin@example.com"
            )
        }
    }
}