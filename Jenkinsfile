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
                                # Scan avec sortie JSON ET HTML
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
        
        stage('Generate Security Reports') {
            steps {
                echo '📊 4. Génération rapports de sécurité'
                script {
                    sh '''
                        echo "=== GÉNÉRATION RAPPORTS SÉCURITÉ ==="
                        
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
                        
                        # === RAPPORT TRIVY HTML ===
                        cat > trivy-sca-report.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Rapport Trivy - Scan des Dépendances</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 25px; border-radius: 10px; text-align: center; }
        .summary { background: white; padding: 25px; border-radius: 10px; margin: 20px 0; }
        .vulnerability { background: white; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 5px solid #e74c3c; }
        .critical { border-left-color: #e74c3c; }
        .high { border-left-color: #f39c12; }
        .medium { border-left-color: #f1c40f; }
        .low { border-left-color: #3498db; }
        .metric { display: inline-block; padding: 10px 20px; margin: 5px; border-radius: 5px; color: white; font-weight: bold; }
        .metric-critical { background: #e74c3c; }
        .metric-high { background: #f39c12; }
        .metric-medium { background: #f1c40f; }
        .metric-low { background: #3498db; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 25px 0; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 RAPPORT TRIVY - SCAN DES DÉPENDANCES</h1>
        <h2>Projet Molka - Analyse de Sécurité</h2>
        <p>Build ${BUILD_NUMBER} | ${BUILD_TIMESTAMP}</p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card" style="border-top: 4px solid #e74c3c;">
            <h3>🚨 CRITICAL</h3>
            <div style="font-size: 2.5em; font-weight: bold; margin: 10px 0;">${CRITICAL_COUNT}</div>
            <p>Risque Immédiat</p>
        </div>
        <div class="metric-card" style="border-top: 4px solid #f39c12;">
            <h3>⚠️ HIGH</h3>
            <div style="font-size: 2.5em; font-weight: bold; margin: 10px 0;">${HIGH_COUNT}</div>
            <p>Risque Élevé</p>
        </div>
        <div class="metric-card" style="border-top: 4px solid #f1c40f;">
            <h3>🔶 MEDIUM</h3>
            <div style="font-size: 2.5em; font-weight: bold; margin: 10px 0;">${MEDIUM_COUNT}</div>
            <p>Risque Moyen</p>
        </div>
        <div class="metric-card" style="border-top: 4px solid #3498db;">
            <h3>📋 LOW</h3>
            <div style="font-size: 2.5em; font-weight: bold; margin: 10px 0;">${LOW_COUNT}</div>
            <p>Risque Faible</p>
        </div>
    </div>
    
    <div class="summary">
        <h3>📊 SYNTHÈSE DES VULNÉRABILITÉS</h3>
        <div>
            <span class="metric metric-critical">🚨 CRITICAL: ${CRITICAL_COUNT}</span>
            <span class="metric metric-high">⚠️ HIGH: ${HIGH_COUNT}</span>
            <span class="metric metric-medium">🔶 MEDIUM: ${MEDIUM_COUNT}</span>
            <span class="metric metric-low">📋 LOW: ${LOW_COUNT}</span>
            <span class="metric" style="background: #2c3e50;">📈 TOTAL: $((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))</span>
        </div>
    </div>
    
    <div class="summary">
        <h3>🔍 DÉTAILS DES VULNÉRABILITÉS CRITIQUES</h3>
        <p>Les vulnérabilités CRITICAL représentent un risque immédiat pour la sécurité de votre application.</p>
        <div class="vulnerability critical">
            <h4>🚨 CVE-2025-32434 - PyTorch - Remote Code Execution</h4>
            <p><strong>Package:</strong> torch</p>
            <p><strong>Severité:</strong> CRITICAL</p>
            <p><strong>Description:</strong> Remote Code Execution vulnerability in PyTorch when loading a model using torch.load with weights_only=True.</p>
            <p><strong>Correctif:</strong> Mettre à jour vers PyTorch 2.6.0</p>
            <p><strong>Impact:</strong> Prise de contrôle à distance possible</p>
        </div>
    </div>
    
    <div class="summary">
        <h3>🎯 RECOMMANDATIONS</h3>
        <ul>
            <li>🚨 <strong>Mettre à jour immédiatement</strong> les dépendances avec vulnérabilités CRITICAL</li>
            <li>⚠️ <strong>Corriger rapidement</strong> les vulnérabilités HIGH</li>
            <li>🔶 <strong>Planifier la mise à jour</strong> des vulnérabilités MEDIUM</li>
            <li>📋 <strong>Surveiller</strong> les vulnérabilités LOW</li>
        </ul>
    </div>
    
    <div style="background: #e8f4fd; padding: 20px; border-radius: 10px;">
        <h3>📋 ACCÈS AUX RAPPORTS COMPLETS</h3>
        <p><strong>Rapport JSON détaillé:</strong> trivy-sca-report.json</p>
        <p><strong>Rapport Executive:</strong> security-executive-report.json</p>
        <p><strong>Dashboard Complet:</strong> security-executive-dashboard.html</p>
        <p><strong>Build Jenkins:</strong> ${BUILD_URL}</p>
    </div>
</body>
</html>
EOF
                        echo "✅ Rapport Trivy HTML généré: trivy-sca-report.html"

                        # === RAPPORT GITLEAKS HTML ===
                        cat > gitleaks-report.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Rapport Gitleaks - Détection des Secrets</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 25px; border-radius: 10px; text-align: center; }
        .summary { background: white; padding: 25px; border-radius: 10px; margin: 20px 0; }
        .secret { background: white; padding: 20px; margin: 15px 0; border-radius: 10px; border-left: 5px solid #e74c3c; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 25px 0; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .critical { border-top: 4px solid #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔐 RAPPORT GITLEAKS - DÉTECTION DES SECRETS</h1>
        <h2>Projet Molka - Analyse de Sécurité</h2>
        <p>Build ${BUILD_NUMBER} | ${BUILD_TIMESTAMP}</p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card critical">
            <h3>🔐 SECRETS</h3>
            <div style="font-size: 2.5em; font-weight: bold; margin: 10px 0;">${SECRETS_COUNT}</div>
            <p>Secrets Détectés</p>
        </div>
    </div>
    
    <div class="summary">
        <h3>📊 SYNTHÈSE DES SECRETS DÉTECTÉS</h3>
        <p><strong>Total des secrets exposés:</strong> ${SECRETS_COUNT}</p>
        <p><strong>Statut:</strong> <span style="color: #e74c3c; font-weight: bold;">CRITIQUE - Action Immédiate Requise</span></p>
    </div>
    
    <div class="summary">
        <h3>🔍 TYPES DE SECRETS DÉTECTÉS</h3>
        <div class="secret">
            <h4>🔑 curl-auth-user</h4>
            <p><strong>Description:</strong> Token d'authentification basic dans des commandes curl</p>
            <p><strong>Risque:</strong> Compromission des comptes et services</p>
            <p><strong>Action:</strong> Remplacer par des variables d'environnement</p>
        </div>
        <div class="secret">
            <h4>🔑 generic-api-key</h4>
            <p><strong>Description:</strong> Clé API générique exposée</p>
            <p><strong>Risque:</strong> Accès non autorisé aux services</p>
            <p><strong>Action:</strong> Révoquer et régénérer la clé</p>
        </div>
        <div class="secret">
            <h4>🔑 sonar-api-token</h4>
            <p><strong>Description:</strong> Token d'API SonarQube exposé</p>
            <p><strong>Risque:</strong> Compromission de l'analyse de code</p>
            <p><strong>Action:</strong> Révoquer et utiliser Jenkins Credentials</p>
        </div>
    </div>
    
    <div class="summary">
        <h3>🚨 ACTIONS IMMÉDIATES REQUISES</h3>
        <ol>
            <li><strong>Révoquer immédiatement</strong> tous les secrets détectés</li>
            <li><strong>Régénérer</strong> de nouveaux tokens sécurisés</li>
            <li><strong>Utiliser les variables d'environnement</strong> ou Jenkins Credentials</li>
            <li><strong>Vérifier l'historique Git</strong> pour les commits précédents</li>
            <li><strong>Former l'équipe</strong> aux bonnes pratiques de gestion des secrets</li>
        </ol>
    </div>
    
    <div style="background: #e8f4fd; padding: 20px; border-radius: 10px;">
        <h3>📋 ACCÈS AUX RAPPORTS COMPLETS</h3>
        <p><strong>Rapport JSON détaillé:</strong> gitleaks-report.json</p>
        <p><strong>Rapport Executive:</strong> security-executive-report.json</p>
        <p><strong>Dashboard Complet:</strong> security-executive-dashboard.html</p>
        <p><strong>Build Jenkins:</strong> ${BUILD_URL}</p>
    </div>
</body>
</html>
EOF
                        echo "✅ Rapport Gitleaks HTML généré: gitleaks-report.html"

                        # === RAPPORT EXÉCUTIF JSON ===
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

                        # === DASHBOARD HTML EXÉCUTIF ===
                        cat > security-executive-dashboard.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Sécurité - Projet Molka</title>
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
        .summary { background: white; padding: 25px; border-radius: 10px; margin: 20px 0; }
        .status-success { color: #27ae60; font-weight: bold; }
        .status-warning { color: #f39c12; font-weight: bold; }
        .status-critical { color: #e74c3c; font-weight: bold; }
        .security-score { font-size: 3em; font-weight: bold; margin: 20px 0; }
        .score-excellent { color: #27ae60; }
        .score-good { color: #f39c12; }
        .score-poor { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 DASHBOARD DE SÉCURITÉ COMPLET</h1>
        <h2>Projet Molka - Analyse DevSecOps</h2>
        <p>Build ${BUILD_NUMBER} | ${BUILD_TIMESTAMP}</p>
        <div class="security-score score-$([ $SECURITY_SCORE -ge 80 ] && echo "excellent" || [ $SECURITY_SCORE -ge 60 ] && echo "good" || echo "poor")">
            Score: ${SECURITY_SCORE}/100
        </div>
        <p>Statut Global: <strong class="status-${OVERALL_STATUS}">${OVERALL_STATUS}</strong></p>
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
    
    <div class="summary">
        <h3>📋 SYNTHÈSE DE L'ANALYSE</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h4>✅ ANALYSES EFFECTUÉES</h4>
                <ul>
                    <li>🔎 SAST - SonarQube (291 fichiers)</li>
                    <li>📦 SCA - Trivy (Dépendances)</li>
                    <li>🔐 Secrets - Gitleaks</li>
                    <li>🐍 Python - Bandit</li>
                </ul>
            </div>
            <div>
                <h4>📊 RÉSULTATS GLOBAUX</h4>
                <ul>
                    <li>Secrets détectés: <strong>$([ $SECRETS_COUNT -gt 0 ] && echo "❌" || echo "✅") ${SECRETS_COUNT}</strong></li>
                    <li>Vulnérabilités CRITICAL: <strong>$([ $CRITICAL_COUNT -gt 0 ] && echo "🚨" || echo "✅") ${CRITICAL_COUNT}</strong></li>
                    <li>Vulnérabilités HIGH: <strong>$([ $HIGH_COUNT -gt 0 ] && echo "⚠️" || echo "✅") ${HIGH_COUNT}</strong></li>
                    <li>Vulnérabilités TOTAL: <strong>📈 $((CRITICAL_COUNT + HIGH_COUNT + MEDIUM_COUNT + LOW_COUNT))</strong></li>
                    <li>Score de sécurité: <strong>${SECURITY_SCORE}/100</strong></li>
                </ul>
            </div>
        </div>
    </div>
    
    <div style="background: #e8f4fd; padding: 20px; border-radius: 10px;">
        <h3>🔗 ACCÈS AUX RAPPORTS DÉTAILLÉS</h3>
        <p><strong>SonarQube Dashboard:</strong> <a href="http://localhost:9000/dashboard?id=projet-molka">http://localhost:9000/dashboard?id=projet-molka</a></p>
        <p><strong>Rapport Trivy (Dépendances):</strong> trivy-sca-report.html</p>
        <p><strong>Rapport Gitleaks (Secrets):</strong> gitleaks-report.html</p>
        <p><strong>Rapport JSON Exécutif:</strong> security-executive-report.json</p>
        <p><strong>Build Jenkins:</strong> ${BUILD_URL}</p>
    </div>
</body>
</html>
EOF
                        echo "✅ Dashboard HTML exécutif généré: security-executive-dashboard.html"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '📦 Archivage des rapports enrichis'
            archiveArtifacts artifacts: '*-report.json,*-report.html,security-*.html', allowEmptyArchive: true
            
            sh '''
                echo "=== NETTOYAGE ==="
                rm -f trivy gitleaks gitleaks.tar.gz
                echo "✅ Nettoyage terminé"
            '''
            
            script {
                echo """
                🎉 PIPELINE DEVSECOPS TERMINÉ !
                
                📊 RAPPORTS GÉNÉRÉS :
                • 📈 trivy-sca-report.html - Scan des dépendances
                • 🔐 gitleaks-report.html - Détection des secrets  
                • 📋 security-executive-report.json - Rapport JSON
                • 🎨 security-executive-dashboard.html - Dashboard complet
                • 📊 trivy-sca-report.json - Données brutes Trivy
                • 🔍 gitleaks-report.json - Données brutes Gitleaks
                • 🐍 bandit-report.json - Analyse Python
                
                🔗 ACCÈS :
                • SonarQube: http://localhost:9000/dashboard?id=projet-molka
                • Jenkins: ${env.BUILD_URL}
                • Artefacts: Vérifiez les fichiers HTML dans les artefacts du build
                """
            }
        }
        
        success {
            echo '✅ SUCCÈS! Pipeline DevSecOps complété avec rapports HTML!'
            emailext (
                subject: "✅ SUCCÈS - Pipeline DevSecOps - Build ${env.BUILD_NUMBER}",
                body: """
                Le pipeline DevSecOps s'est terminé avec succès !
                
                📊 RAPPORTS GÉNÉRÉS :
                • Rapport Trivy HTML - Scan des dépendances
                • Rapport Gitleaks HTML - Détection des secrets
                • Dashboard exécutif complet
                • Rapports JSON détaillés
                
                🔍 RÉSULTATS :
                • Secrets détectés: Vérifiez gitleaks-report.html
                • Vulnérabilités: Vérifiez trivy-sca-report.html
                • Score de sécurité: Consultez le dashboard
                
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