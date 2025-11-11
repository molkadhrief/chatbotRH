pipeline {
    agent any 
    
    environment {
        SONARQUBE_URL = 'http://localhost:9000'
    }
    
    stages {
        stage('Checkout & Setup') {
            steps { 
                echo '🔍 1. Checkout et configuration'
                checkout scm 
                
                script {
                    bat '''
                        echo "=== VÉRIFICATION CONFIGURATION TEMPS RÉEL ==="
                        echo "Fichiers de configuration:"
                        dir /b | findstr ".bandit .eslintrc.json"
                        
                        echo "Outils installés:"
                        python -m pip list | findstr "bandit semgrep"
                        npm list -g | findstr "eslint" || echo "ESLint non installé"
                    '''
                }
            }
        }
        
        stage('Real-time Security Analysis') {
            steps {
                echo '🛡️ 2. Analyse sécurité temps réel ACTIVE'
                script {
                    bat '''
                        echo "=== DÉTECTION TEMPS RÉEL ACTIVE ==="
                        
                        # 1. SCAN BANDIT AVEC CONFIG
                        echo "🔍 Bandit avec configuration .bandit..."
                        if exist .bandit (
                            echo "✅ Fichier .bandit détecté"
                            bandit -c .bandit -r . -f json -o bandit-realtime-report.json
                        ) else (
                            bandit -r . -f json -o bandit-realtime-report.json
                        )
                        
                        # 2. SCAN SEMGREP
                        echo "📝 Semgrep - Scan patterns..."
                        python -m semgrep --config=auto --json --output semgrep-realtime-report.json . || echo "Scan Semgrep terminé"
                        
                        # 3. SCAN SECRETS
                        echo "🔐 Détection des secrets..."
                        findstr /S /I "password secret key token api_key" *.py *.js *.txt *.yml *.yaml 2>nul > secrets-scan.txt || echo "Aucun secret évident trouvé"
                        
                        # 4. ANALYSE DES RÉSULTATS EN TEMPS RÉEL
                        echo "📊 ANALYSE TEMPS RÉEL:"
                        
                        if exist bandit-realtime-report.json (
                            python -c "import json; data=json.load(open('bandit-realtime-report.json')); print(f'🚨 Bandit - HIGH: {data[\"metrics\"][\"_totals\"][\"HIGH\"]}, MEDIUM: {data[\"metrics\"][\"_totals\"][\"MEDIUM\"]}')"
                        )
                        
                        if exist semgrep-realtime-report.json (
                            python -c "import json; data=json.load(open('semgrep-realtime-report.json')); print(f'📝 Semgrep - Problèmes: {len(data[\"results\"])}')"
                        )
                        
                        if exist secrets-scan.txt (
                            echo "🔐 Secrets potentiels:"
                            type secrets-scan.txt | head -5
                        )
                    '''
                }
            }
        }
        
        stage('Generate Real-time Dashboard') {
            steps {
                echo '📈 3. Dashboard temps réel'
                script {
                    bat '''
                        echo "=== CRÉATION DASHBOARD TEMPS RÉEL ==="
                        
                        python -c "
import json
import os
from datetime import datetime

# Collecte des métriques
metrics = {
    'bandit_high': 0,
    'bandit_medium': 0, 
    'semgrep_issues': 0,
    'secrets_found': 0,
    'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

try:
    if os.path.exists('bandit-realtime-report.json'):
        with open('bandit-realtime-report.json', 'r') as f:
            data = json.load(f)
            metrics['bandit_high'] = data.get('metrics', {}).get('_totals', {}).get('HIGH', 0)
            metrics['bandit_medium'] = data.get('metrics', {}).get('_totals', {}).get('MEDIUM', 0)
except Exception as e:
    print(f'Erreur Bandit: {e}')

try:
    if os.path.exists('semgrep-realtime-report.json'):
        with open('semgrep-realtime-report.json', 'r') as f:
            data = json.load(f)
            metrics['semgrep_issues'] = len(data.get('results', []))
except Exception as e:
    print(f'Erreur Semgrep: {e}')

try:
    if os.path.exists('secrets-scan.txt'):
        with open('secrets-scan.txt', 'r') as f:
            metrics['secrets_found'] = len(f.readlines())
except Exception as e:
    print(f'Erreur secrets: {e}')

# Génération HTML - CORRIGÉ : utilisation de guillemets simples
html = '''<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Sécurité Temps Réel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-5px); }
        .critical { border-top: 5px solid #e74c3c; }
        .warning { border-top: 5px solid #f39c12; }
        .success { border-top: 5px solid #27ae60; }
        .metric-value { font-size: 3em; font-weight: bold; margin: 10px 0; }
        .live-badge { background: #e74c3c; color: white; padding: 5px 10px; border-radius: 15px; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>🛡️ Dashboard Sécurité Temps Réel</h1>
        <h2>Projet Molka - Scan Live</h2>
        <p><span class=\"live-badge\">LIVE</span> Dernier scan: ''' + metrics['scan_time'] + '''</p>
    </div>
    
    <div class=\"metrics\">
        <div class=\"metric-card ''' + ('critical' if metrics['bandit_high'] > 0 else 'success') + '''\">
            <h3>🐍 Bandit HIGH</h3>
            <div class=\"metric-value\">''' + str(metrics['bandit_high']) + '''</div>
            <p>Vulnérabilités critiques Python</p>
        </div>
        
        <div class=\"metric-card ''' + ('warning' if metrics['bandit_medium'] > 0 else 'success') + '''\">
            <h3>🐍 Bandit MEDIUM</h3>
            <div class=\"metric-value\">''' + str(metrics['bandit_medium']) + '''</div>
            <p>Vulnérabilités moyennes Python</p>
        </div>
        
        <div class=\"metric-card ''' + ('warning' if metrics['semgrep_issues'] > 0 else 'success') + '''\">
            <h3>📝 Semgrep</h3>
            <div class=\"metric-value\">''' + str(metrics['semgrep_issues']) + '''</div>
            <p>Patterns de vulnérabilités</p>
        </div>
        
        <div class=\"metric-card ''' + ('critical' if metrics['secrets_found'] > 0 else 'success') + '''\">
            <h3>🔐 Secrets</h3>
            <div class=\"metric-value\">''' + str(metrics['secrets_found']) + '''</div>
            <p>Secrets potentiels</p>
        </div>
    </div>
    
    <div style=\"background: white; padding: 20px; border-radius: 10px; margin-top: 20px;\">
        <h3>🔧 Détection Temps Réel Active</h3>
        <ul>
            <li>✅ <strong>Bandit:</strong> Analyse sécurité Python en temps réel</li>
            <li>✅ <strong>Semgrep:</strong> Scan patterns de vulnérabilités</li>
            <li>✅ <strong>Secrets Scan:</strong> Détection mots de passe hardcodés</li>
            <li>✅ <strong>Config personnalisée:</strong> Fichiers .bandit et .eslintrc.json</li>
        </ul>
    </div>
</body>
</html>'''

with open('realtime-security-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ Dashboard temps réel généré: realtime-security-dashboard.html')
"

                        echo "✅ Dashboard généré avec données temps réel"
                    '''
                }
            }
        }
        
        stage('SAST - SonarQube Integration') {
            steps {
                echo '🔎 4. Intégration SonarQube'
                withSonarQubeEnv('sonar-server') {
                    script {
                        withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                            bat '''
                                echo "🚀 SonarQube avec métriques temps réel..."
                                sonar-scanner ^
                                -Dsonar.projectKey=projet-molka ^
                                -Dsonar.sources=. ^
                                -Dsonar.projectName=\"Projet Molka - Détection Temps Réel\" ^
                                -Dsonar.host.url=http://localhost:9000 ^
                                -Dsonar.token=%SONAR_TOKEN% ^
                                -Dsonar.sourceEncoding=UTF-8
                            '''
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo '📊 Archivage rapports temps réel'
            archiveArtifacts artifacts: '*-report.*,realtime-security-dashboard.html,secrets-scan.txt', allowEmptyArchive: true
            
            script {
                echo """
                🎉 DÉTECTION TEMPS RÉEL TERMINÉE!
                
                📊 MÉTRIQUES COLLECTÉES:
                • 🐍 Bandit: Sécurité Python avec config .bandit
                • 📝 Semgrep: Patterns vulnérabilités  
                • 🔐 Secrets: Mots de passe hardcodés
                • 📈 Dashboard: Visualisation temps réel
                
                🌐 ACCÈS:
                • Dashboard: realtime-security-dashboard.html
                • SonarQube: http://localhost:9000/dashboard?id=projet-molka
                • Jenkins: ${env.BUILD_URL}
                
                🔧 CONFIGURATION TEMPS RÉEL:
                ✅ .bandit - Configuration Bandit
                ✅ .eslintrc.json - Configuration ESLint  
                """
            }
        }
        
        success {
            echo '✅ DÉTECTION TEMPS RÉEL ACTIVE - Pipeline réussi!'
        }
    }
}