pipeline {
    agent any 
    
    environment {
        SONARQUBE_URL = 'http://localhost:9000'
        PYTHON_PATH = 'python'
        PROJECT_DIR = '.'
    }
    
    stages {
        stage('Checkout & Environment Setup') {
            steps { 
                echo '🔍 1. Checkout et configuration environnement'
                checkout scm 
                
                script {
                    // Vérification de l'environnement
                    bat '''
                        echo "=== ENVIRONNEMENT WINDOWS ==="
                        python --version
                        pip --version
                        echo "Répertoire: %CD%"
                        dir
                    '''
                }
            }
        }
        
        stage('Install Security Tools') {
            steps {
                echo '🛠️ 2. Installation outils sécurité Windows'
                script {
                    bat '''
                        echo "=== INSTALLATION OUTILS SÉCURITÉ ==="
                        
                        # Installation Bandit pour Python
                        pip install bandit safety
                        
                        # Installation Semgrep
                        pip install semgrep
                        
                        # Installation Gitleaks (version Windows)
                        curl -L -o gitleaks.zip https://github.com/gitleaks/gitleaks/releases/download/v8.29.0/gitleaks_8.29.0_windows_x64.zip
                        7z x gitleaks.zip -ogitleaks
                        move gitleaks\\gitleaks.exe .
                        
                        echo "✅ Outils sécurité installés"
                    '''
                }
            }
        }
        
        stage('Real-time Security Analysis') {
            steps {
                echo '🛡️ 3. Analyse sécurité temps réel'
                script {
                    bat '''
                        echo "=== ANALYSE SÉCURITÉ TEMPS RÉEL ==="
                        
                        # 1. SCAN BANDIT - Sécurité Python
                        echo "🔍 Bandit - Analyse sécurité Python..."
                        if exist *.py (
                            bandit -r . -f json -o bandit-report.json
                            if %errorlevel% neq 0 (
                                echo "⚠️  Bandit a trouvé des problèmes"
                            )
                        ) else (
                            echo "ℹ️  Aucun fichier Python trouvé"
                        )
                        
                        # 2. SCAN SEMGREP - Patterns de vulnérabilités
                        echo "📝 Semgrep - Scan patterns sécurité..."
                        semgrep --config=auto --json --output semgrep-report.json . || echo "Semgrep scan completed"
                        
                        # 3. SCAN SECRETS - Gitleaks
                        echo "🔐 Gitleaks - Détection des secrets..."
                        gitleaks.exe detect --source . --report-format json --report-path gitleaks-report.json --exit-code 0
                        
                        # 4. SCAN DE SÉCURITÉ CUSTOM
                        echo "🎯 Scan vulnérabilités custom..."
                        
                        # Scan des mots de passe hardcodés
                        findstr /S /I "password secret key token" *.py *.js *.html *.txt 2>nul | head -10 > custom-scan.txt || echo "Aucun secret évident trouvé"
                        
                        # Scan des fonctions dangereuses
                        findstr /S /I "eval exec subprocess os.system" *.py 2>nul | head -5 >> custom-scan.txt || echo "Aucune fonction dangereuse trouvée"
                        
                        echo "✅ Analyse temps réel terminée"
                    '''
                }
            }
        }
        
        stage('Security Results Analysis') {
            steps {
                echo '📊 4. Analyse des résultats sécurité'
                script {
                    bat '''
                        echo "=== ANALYSE DES RÉSULTATS ==="
                        
                        # Analyse Bandit
                        if exist bandit-report.json (
                            echo "📊 RÉSULTATS BANDIT:"
                            python -c "import json; data=json.load(open('bandit-report.json')); print(f'HIGH: {data[\"metrics\"][\"_totals\"][\"HIGH\"]}, MEDIUM: {data[\"metrics\"][\"_totals\"][\"MEDIUM\"]}')" 2>nul || echo "Erreur analyse Bandit"
                        )
                        
                        # Analyse Semgrep
                        if exist semgrep-report.json (
                            echo "📊 RÉSULTATS SEMGREP:"
                            python -c "import json; data=json.load(open('semgrep-report.json')); print(f'Problèmes: {len(data[\"results\"])}')" 2>nul || echo "Erreur analyse Semgrep"
                        )
                        
                        # Analyse Gitleaks
                        if exist gitleaks-report.json (
                            echo "📊 RÉSULTATS GITLEAKS:"
                            python -c "import json; data=json.load(open('gitleaks-report.json')); print(f'Secrets: {len(data)}')" 2>nul || echo "Erreur analyse Gitleaks"
                        )
                        
                        # Affichage scan custom
                        if exist custom-scan.txt (
                            echo "📊 RÉSULTATS SCAN CUSTOM:"
                            type custom-scan.txt
                        )
                    '''
                }
            }
        }
        
        stage('SAST - SonarQube Analysis') {
            steps {
                echo '🔎 5. SAST - Analyse SonarQube'
                withSonarQubeEnv('sonar-server') {
                    script {
                        withCredentials([string(credentialsId: 'sonar-token-molka', variable: 'SONAR_TOKEN')]) {
                            bat '''
                                echo "🚀 Lancement analyse SonarQube..."
                                sonar-scanner ^
                                -Dsonar.projectKey=projet-molka ^
                                -Dsonar.sources=. ^
                                -Dsonar.projectName="Projet Molka DevSecOps" ^
                                -Dsonar.host.url=http://localhost:9000 ^
                                -Dsonar.token=%SONAR_TOKEN% ^
                                -Dsonar.sourceEncoding=UTF-8
                                echo "✅ Analyse SonarQube terminée"
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Generate Security Dashboard') {
            steps {
                echo '📈 6. Génération dashboard sécurité'
                script {
                    bat '''
                        echo "=== GÉNÉRATION DASHBOARD ==="
                        
                        # Lecture des métriques
                        python -c "
import json
import os

# Initialisation des métriques
secrets_count = 0
bandit_high = 0
bandit_medium = 0
semgrep_issues = 0

try:
    if os.path.exists('gitleaks-report.json'):
        with open('gitleaks-report.json', 'r') as f:
            data = json.load(f)
            secrets_count = len(data)
except:
    pass

try:
    if os.path.exists('bandit-report.json'):
        with open('bandit-report.json', 'r') as f:
            data = json.load(f)
            bandit_high = data.get('metrics', {}).get('_totals', {}).get('HIGH', 0)
            bandit_medium = data.get('metrics', {}).get('_totals', {}).get('MEDIUM', 0)
except:
    pass

try:
    if os.path.exists('semgrep-report.json'):
        with open('semgrep-report.json', 'r') as f:
            data = json.load(f)
            semgrep_issues = len(data.get('results', []))
except:
    pass

print(f'SECRETS_COUNT={secrets_count}')
print(f'BANDIT_HIGH={bandit_high}')
print(f'BANDIT_MEDIUM={bandit_medium}')
print(f'SEMGREP_ISSUES={semgrep_issues}')
" > security-metrics.txt

                        # Génération dashboard HTML
                        python -c "
import os

# Lecture des métriques
metrics = {}
with open('security-metrics.txt', 'r') as f:
    for line in f:
        if '=' in line:
            key, value = line.strip().split('=')
            metrics[key] = value

html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Sécurité - Projet Molka</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric-card {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
        .critical {{ border-left: 5px solid #e74c3c; }}
        .warning {{ border-left: 5px solid #f39c12; }}
        .success {{ border-left: 5px solid #27ae60; }}
    </style>
</head>
<body>
    <div class=\"header\">
        <h1>🛡️ Dashboard Sécurité Temps Réel</h1>
        <h2>Projet Molka - Windows Environment</h2>
    </div>
    
    <div class=\"metrics\">
        <div class=\"metric-card {'critical' if int(metrics.get('SECRETS_COUNT', 0)) > 0 else 'success'}\">
            <h3>🔐 Secrets</h3>
            <div style=\"font-size: 2.5em; font-weight: bold;\">{metrics.get('SECRETS_COUNT', 0)}</div>
            <p>Secrets détectés</p>
        </div>
        
        <div class=\"metric-card {'critical' if int(metrics.get('BANDIT_HIGH', 0)) > 0 else 'success'}\">
            <h3>🚨 Bandit HIGH</h3>
            <div style=\"font-size: 2.5em; font-weight: bold;\">{metrics.get('BANDIT_HIGH', 0)}</div>
            <p>Vulnérabilités Python</p>
        </div>
        
        <div class=\"metric-card {'warning' if int(metrics.get('BANDIT_MEDIUM', 0)) > 0 else 'success'}\">
            <h3>⚠️ Bandit MEDIUM</h3>
            <div style=\"font-size: 2.5em; font-weight: bold;\">{metrics.get('BANDIT_MEDIUM', 0)}</div>
            <p>Vulnérabilités Python</p>
        </div>
        
        <div class=\"metric-card {'warning' if int(metrics.get('SEMGREP_ISSUES', 0)) > 0 else 'success'}\">
            <h3>📝 Semgrep</h3>
            <div style=\"font-size: 2.5em; font-weight: bold;\">{metrics.get('SEMGREP_ISSUES', 0)}</div>
            <p>Patterns détectés</p>
        </div>
    </div>
</body>
</html>
'''

with open('security-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
"

                        echo "✅ Dashboard généré: security-dashboard.html"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo '📦 Archivage des rapports'
            archiveArtifacts artifacts: '*-report.*,security-dashboard.html,security-metrics.txt,custom-scan.txt', allowEmptyArchive: true
            
            // Nettoyage
            bat '''
                del gitleaks.exe
                del gitleaks.zip
                echo "✅ Nettoyage terminé"
            '''
            
            script {
                echo """
                🎉 ANALYSE SÉCURITÉ TEMPS RÉEL TERMINÉE!
                
                📊 OUTILS UTILISÉS:
                • 🐍 Bandit: Sécurité Python
                • 📝 Semgrep: Patterns vulnérabilités  
                • 🔐 Gitleaks: Détection secrets
                • 🎯 Custom Scan: Vulnérabilités spécifiques
                
                📁 RAPPORTS:
                • security-dashboard.html
                • bandit-report.json
                • semgrep-report.json  
                • gitleaks-report.json
                • custom-scan.txt
                
                🔗 SONARQUBE:
                • http://localhost:9000/dashboard?id=projet-molka
                """
            }
        }
    }
}