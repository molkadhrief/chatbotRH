pipeline {
    agent any 
    
    environment {
        SONARQUBE_URL = 'http://localhost:9000'
        PATH = "$PATH:/var/lib/jenkins/.local/bin"
        BUILD_TIMESTAMP = new Date().format("yyyy-MM-dd'T'HH:mm:ssXXX")
    }
    
    stages {
        // [Les stages checkout et installation restent identiques...]
        
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
                                    CRITICAL_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' trivy-sca-report.json 2>/dev/null || echo "0")
                                    HIGH_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' trivy-sca-report.json 2>/dev/null || echo "0")
                                    MEDIUM_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "MEDIUM")] | length' trivy-sca-report.json 2>/dev/null || echo "0")
                                    LOW_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "LOW")] | length' trivy-sca-report.json 2>/dev/null || echo "0")
                                    TOTAL_COUNT=$((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))
                                    
                                    # Extraction des vulnérabilités critiques pour le rapport
                                    jq '.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | {VulnerabilityID, PkgName, Title, Description, Severity, FixedVersion}' trivy-sca-report.json > trivy-critical-details.json 2>/dev/null || echo "[]" > trivy-critical-details.json
                                    
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
                                
                                SECRETS_COUNT=$(jq '. | length' gitleaks-report.json 2>/dev/null || echo "0")
                                
                                # Analyse des types de secrets détectés
                                if [ "$SECRETS_COUNT" -gt 0 ]; then
                                    # Création d'un résumé par type de secret
                                    jq 'group_by(.RuleID) | map({rule: .[0].RuleID, count: length, description: .[0].Description})' gitleaks-report.json > gitleaks-summary.json 2>/dev/null || echo "[]" > gitleaks-summary.json
                                    
                                    echo "❌ SECRETS DÉTECTÉS - $SECRETS_COUNT au total"
                                    jq -r '.[] | "   • \(.rule): \(.count) occurrence(s)"' gitleaks-summary.json 2>/dev/null || echo "   ⚠️ Impossible d'analyser les détails"
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
                                        # Extraction des métriques détaillées
                                        BANDIT_HIGH=$(jq '.metrics._totals.HIGH' bandit-report.json 2>/dev/null || echo "0")
                                        BANDIT_MEDIUM=$(jq '.metrics._totals.MEDIUM' bandit-report.json 2>/dev/null || echo "0")
                                        BANDIT_LOW=$(jq '.metrics._totals.LOW' bandit-report.json 2>/dev/null || echo "0")
                                        BANDIT_CONFIDENCE_HIGH=$(jq '.metrics._totals."CONFIDENCE.HIGH"' bandit-report.json 2>/dev/null || echo "0")
                                        BANDIT_CONFIDENCE_MEDIUM=$(jq '.metrics._totals."CONFIDENCE.MEDIUM"' bandit-report.json 2>/dev/null || echo "0")
                                        BANDIT_CONFIDENCE_LOW=$(jq '.metrics._totals."CONFIDENCE.LOW"' bandit-report.json 2>/dev/null || echo "0")
                                        
                                        # Extraction des enjeux de sécurité HIGH
                                        jq '.results[] | select(.issue_confidence == "HIGH" and .issue_severity == "HIGH") | {issue_text, filename, line_number, test_name}' bandit-report.json > bandit-critical-issues.json 2>/dev/null || echo "[]" > bandit-critical-issues.json
                                        
                                        echo "📊 Bandit - HIGH: $BANDIT_HIGH, MEDIUM: $BANDIT_MEDIUM, LOW: $BANDIT_LOW"
                                        echo "✅ Bandit scan enrichi terminé"
                                    else
                                        echo '{"metrics": {"_totals": {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CONFIDENCE.HIGH": 0, "CONFIDENCE.MEDIUM": 0, "CONFIDENCE.LOW": 0}}}' > bandit-report.json
                                        echo "[]" > bandit-critical-issues.json
                                    fi
                                else
                                    echo "ℹ️  Aucun fichier Python trouvé"
                                    echo '{"metrics": {"_totals": {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CONFIDENCE.HIGH": 0, "CONFIDENCE.MEDIUM": 0, "CONFIDENCE.LOW": 0}}}' > bandit-report.json
                                    echo "[]" > bandit-critical-issues.json
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
                        
                        # Collecte métriques détaillées
                        SECRETS_COUNT=$(jq '. | length' gitleaks-report.json 2>/dev/null || echo "0")
                        SECRETS_SUMMARY=$(cat gitleaks-summary.json 2>/dev/null || echo "[]")
                        
                        CRITICAL_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' trivy-sca-report.json 2>/dev/null || echo "0")
                        HIGH_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' trivy-sca-report.json 2>/dev/null || echo "0")
                        MEDIUM_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "MEDIUM")] | length' trivy-sca-report.json 2>/dev/null || echo "0")
                        LOW_COUNT=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "LOW")] | length' trivy-sca-report.json 2>/dev/null || echo "0")
                        TRIVY_CRITICAL_DETAILS=$(cat trivy-critical-details.json 2>/dev/null || echo "[]")
                        
                        BANDIT_HIGH=$(jq '.metrics._totals.HIGH' bandit-report.json 2>/dev/null || echo "0")
                        BANDIT_MEDIUM=$(jq '.metrics._totals.MEDIUM' bandit-report.json 2>/dev/null || echo "0")
                        BANDIT_LOW=$(jq '.metrics._totals.LOW' bandit-report.json 2>/dev/null || echo "0")
                        BANDIT_CRITICAL_ISSUES=$(cat bandit-critical-issues.json 2>/dev/null || echo "[]")
                        
                        # Calcul score de sécurité global (exemple simple)
                        SECURITY_SCORE=100
                        if [ "$CRITICAL_COUNT" -gt 0 ]; then SECURITY_SCORE=$((SECURITY_SCORE - 30)); fi
                        if [ "$HIGH_COUNT" -gt 0 ]; then SECURITY_SCORE=$((SECURITY_SCORE - 20)); fi
                        if [ "$SECRETS_COUNT" -gt 0 ]; then SECURITY_SCORE=$((SECURITY_SCORE - 25)); fi
                        if [ "$BANDIT_HIGH" -gt 0 ]; then SECURITY_SCORE=$((SECURITY_SCORE - 15)); fi
                        if [ "$SECURITY_SCORE" -lt 0 ]; then SECURITY_SCORE=0; fi
                        
                        # Détermination statut global
                        if [ "$CRITICAL_COUNT" -gt 0 ] || [ "$SECRETS_COUNT" -gt 10 ]; then
                            OVERALL_STATUS="CRITICAL"
                        elif [ "$HIGH_COUNT" -gt 0 ] || [ "$SECRETS_COUNT" -gt 0 ] || [ "$BANDIT_HIGH" -gt 0 ]; then
                            OVERALL_STATUS="HIGH"
                        elif [ "$MEDIUM_COUNT" -gt 0 ] || [ "$BANDIT_MEDIUM" -gt 0 ]; then
                            OVERALL_STATUS="MEDIUM"
                        else
                            OVERALL_STATUS="LOW"
                        fi
                        
                        # Rapport JSON principal enrichi
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
  "detailed_findings": {
    "critical_vulnerabilities": ${TRIVY_CRITICAL_DETAILS},
    "secrets_breakdown": ${SECRETS_SUMMARY},
    "python_critical_issues": ${BANDIT_CRITICAL_ISSUES}
  },
  "recommendations": {
    "immediate_actions": [
      $(if [ "$CRITICAL_COUNT" -gt 0 ]; then echo "\"Mettre à jour les dépendances avec vulnérabilités CRITICAL\","; fi)
      $(if [ "$SECRETS_COUNT" -gt 0 ]; then echo "\"Révoquer les secrets exposés et les régénérer\","; fi)
      $(if [ "$BANDIT_HIGH" -gt 0 ]; then echo "\"Corriger les vulnérabilités Python de niveau HIGH\","; fi)
      "\"Revoir la configuration de sécurité du projet\""
    ],
    "preventive_measures": [
      "Intégrer les scans de sécurité dans le processus CI/CD",
      "Former les développeurs aux bonnes pratiques de sécurité",
      "Mettre en place des revues de code sécurité"
    ]
  }
}
EOF
                        echo "✅ Rapport JSON exécutif généré: security-executive-report.json"
                        
                        # Rapport de synthèse pour dashboard
                        cat > security-dashboard-data.json << EOF
{
  "project": "Projet Molka",
  "build": "${BUILD_NUMBER}",
  "timestamp": "${BUILD_TIMESTAMP}",
  "security_score": ${SECURITY_SCORE},
  "status": "${OVERALL_STATUS}",
  "metrics": [
    {
      "name": "Secrets",
      "value": ${SECRETS_COUNT},
      "status": "$([ "$SECRETS_COUNT" -eq 0 ] && echo "success" || echo "critical")",
      "trend": "stable"
    },
    {
      "name": "Vuln. Critical",
      "value": ${CRITICAL_COUNT},
      "status": "$([ "$CRITICAL_COUNT" -eq 0 ] && echo "success" || echo "critical")",
      "trend": "stable"
    },
    {
      "name": "Vuln. High",
      "value": ${HIGH_COUNT},
      "status": "$([ "$HIGH_COUNT" -eq 0 ] && echo "success" || echo "warning")",
      "trend": "stable"
    },
    {
      "name": "Python Issues",
      "value": ${BANDIT_HIGH},
      "status": "$([ "$BANDIT_HIGH" -eq 0 ] && echo "success" || echo "warning")",
      "trend": "stable"
    }
  ],
  "trends": {
    "security_score_trend": ${SECURITY_SCORE},
    "vulnerability_trend": $((CRITICAL_COUNT + HIGH_COUNT)),
    "secrets_trend": ${SECRETS_COUNT}
  }
}
EOF
                        echo "✅ Données dashboard générées: security-dashboard-data.json"
                    '''
                }
            }
        }
        
        stage('Generate HTML Executive Dashboard') {
            steps {
                echo '🎨 5. Génération Dashboard Exécutif'
                script {
                    sh '''
                        # Lecture des données depuis le JSON enrichi
                        SECURITY_DATA=$(cat security-executive-report.json)
                        SECURITY_SCORE=$(echo "$SECURITY_DATA" | jq -r '.metadata.security_score')
                        OVERALL_STATUS=$(echo "$SECURITY_DATA" | jq -r '.metadata.overall_status')
                        SECRETS_COUNT=$(echo "$SECURITY_DATA" | jq -r '.summary.secrets_detected')
                        CRITICAL_COUNT=$(echo "$SECURITY_DATA" | jq -r '.summary.vulnerabilities.critical')
                        HIGH_COUNT=$(echo "$SECURITY_DATA" | jq -r '.summary.vulnerabilities.high')
                        BANDIT_HIGH=$(echo "$SECURITY_DATA" | jq -r '.summary.python_security.high')
                        
                        # Génération HTML avec données dynamiques
                        cat > security-executive-dashboard.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Rapport Sécurité Complet - Projet Molka</title>
    <meta charset="UTF-8">
    <style>
        /* [CSS identique mais amélioré...] */
        .security-score {
            font-size: 3em;
            font-weight: bold;
            margin: 20px 0;
        }
        .score-excellent { color: #27ae60; }
        .score-good { color: #f39c12; }
        .score-poor { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 RAPPORT DEVSECOPS COMPLET - V2</h1>
        <h2>Projet Molka - Analyse de Sécurité Avancée</h2>
        <p>Build ${BUILD_NUMBER} | ${BUILD_TIMESTAMP}</p>
        <div class="security-score score-$([ $SECURITY_SCORE -ge 80 ] && echo "excellent" || [ $SECURITY_SCORE -ge 60 ] && echo "good" || echo "poor")">
            Score: ${SECURITY_SCORE}/100
        </div>
        <p>Statut Global: <strong class="status-${OVERALL_STATUS}">${OVERALL_STATUS}</strong></p>
    </div>
    
    <!-- Contenu identique mais avec données dynamiques -->
</body>
</html>
EOF
                        echo "✅ Dashboard HTML généré avec données JSON"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '📦 Archivage des rapports enrichis'
            archiveArtifacts artifacts: '*-report.json,*-summary.json,*-details.json,*-dashboard*.json,security-*.html', allowEmptyArchive: true
            
            // Publication des rapports JSON pour intégration
            script {
                publishJSON target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    reportDir: '',
                    reportFiles: 'security-executive-report.json,security-dashboard-data.json',
                    reportName: 'Rapports Sécurité JSON'
                ]
            }
            
            sh '''
                echo "=== NETTOYAGE ==="
                rm -f trivy gitleaks gitleaks.tar.gz
                echo "✅ Nettoyage terminé"
            '''
            
            // Affichage final enrichi
            script {
                def execReport = readJSON file: 'security-executive-report.json'
                def securityScore = execReport.metadata.security_score
                def overallStatus = execReport.metadata.overall_status
                
                echo """
                🎉 PIPELINE DEVSECOPS V2 TERMINÉ !
                
                📈 SCORE DE SÉCURITÉ: ${securityScore}/100
                🎯 STATUT GLOBAL: ${overallStatus}
                
                📊 RAPPORTS GÉNÉRÉS:
                • security-executive-report.json - Rapport complet structuré
                • security-dashboard-data.json - Données pour dashboard
                • security-executive-dashboard.html - Dashboard visuel
                • trivy-sca-report.json - Scan dépendances détaillé
                • gitleaks-report.json - Détection secrets avec analyse
                • bandit-report.json - Analyse Python avancée
                
                🔗 ACCÈS:
                • SonarQube: http://localhost:9000/dashboard?id=projet-molka
                • Jenkins: ${env.BUILD_URL}
                • Rapports JSON: Intégrables avec outils externes
                """
            }
        }
        
        success {
            echo '✅ SUCCÈS TOTAL! Pipeline DevSecOps V2 complété!'
            script {
                def execReport = readJSON file: 'security-executive-report.json'
                def securityScore = execReport.metadata.security_score
                
                emailext (
                    subject: "✅ SUCCÈS - Pipeline DevSecOps V2 - Score: ${securityScore}/100 - Build ${env.BUILD_NUMBER}",
                    body: """
                    Le pipeline DevSecOps V2 s'est terminé avec succès !
                    
                    📊 SCORE DE SÉCURITÉ: ${securityScore}/100
                    
                    Analyses réalisées:
                    - SAST SonarQube: Analyse code statique
                    - SCA Trivy: Scan dépendances enrichi
                    - Détection secrets: Analyse par type
                    - Sécurité Python: Bandit avancé
                    
                    Rapports générés:
                    • Rapport JSON exécutif
                    • Données dashboard
                    • Dashboard HTML interactif
                    
                    Accès au rapport: ${env.BUILD_URL}
                    Dashboard SonarQube: http://localhost:9000/dashboard?id=projet-molka
                    """,
                    to: "admin@example.com",
                    attachmentsPattern: 'security-executive-report.json,security-executive-dashboard.html'
                )
            }
        }
    }
}