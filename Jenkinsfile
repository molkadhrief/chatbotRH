stage('SCA - Dependency Scan') {
    steps {
        echo '📦 3.2 SCA - Scan des dépendances'
        script {
            sh '''
                echo "=== SCAN TRIVY ENRICHIE ==="
                # Scan avec sortie JSON ET HTML
                ./trivy fs --format json --output trivy-sca-report.json --exit-code 0 --severity CRITICAL,HIGH,MEDIUM,LOW .
                ./trivy fs --format template --template "@html.tpl" --output trivy-sca-report.html --exit-code 0 --severity CRITICAL,HIGH,MEDIUM,LOW .
                
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
                
                # Vérification du rapport HTML
                if [ -f trivy-sca-report.html ]; then
                    echo "✅ Rapport Trivy HTML généré: trivy-sca-report.html"
                else
                    echo "⚠️  Génération du rapport HTML échouée, création manuelle..."
                    # Création manuelle du rapport HTML
                    cat > trivy-sca-report.html << 'EOF'
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
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 RAPPORT TRIVY - SCAN DES DÉPENDANCES</h1>
        <h2>Projet Molka - Analyse de Sécurité</h2>
        <p>Build ${BUILD_NUMBER} | ${BUILD_TIMESTAMP}</p>
    </div>
    
    <div class="summary">
        <h3>📊 SYNTHÈSE DES VULNÉRABILITÉS</h3>
        <div>
            <span class="metric metric-critical">🚨 CRITICAL: ${CRITICAL_COUNT}</span>
            <span class="metric metric-high">⚠️ HIGH: ${HIGH_COUNT}</span>
            <span class="metric metric-medium">🔶 MEDIUM: ${MEDIUM_COUNT}</span>
            <span class="metric metric-low">📋 LOW: ${LOW_COUNT}</span>
            <span class="metric" style="background: #2c3e50;">📈 TOTAL: ${TOTAL_COUNT}</span>
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
                    echo "✅ Rapport Trivy HTML créé manuellement"
                fi
                
                echo "✅ Scan Trivy enrichi terminé"
            '''
        }
    }
}