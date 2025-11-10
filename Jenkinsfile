pipeline {
    agent any 

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
                    // Installation SonarScanner
                    sh '''
                        echo "=== INSTALLATION SONARSCANNER ==="
                        # Télécharger et installer sonar-scanner
                        wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-linux.zip
                        unzip sonar-scanner-cli-5.0.1.3006-linux.zip
                        mv sonar-scanner-5.0.1.3006-linux sonar-scanner
                        export PATH=$PWD/sonar-scanner/bin:$PATH
                        sonar-scanner --version
                        echo "✅ sonar-scanner installé"
                    '''
                    
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
                    sh '''
                        echo "🚀 Lancement de l'analyse SonarQube..."
                        export PATH=$PWD/sonar-scanner/bin:$PATH
                        sonar-scanner \
                        -Dsonar.projectKey=projet-molka \
                        -Dsonar.sources=. \
                        -Dsonar.projectName="Projet Molka" \
                        -Dsonar.projectVersion=1.0 \
                        -Dsonar.sourceEncoding=UTF-8
                    '''
                }
            }
        }

        // ... reste de votre pipeline ...
    }
}