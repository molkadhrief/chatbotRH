pipeline {
    agent any

    // ON REMET LA SECTION 'tools' AVEC LA SYNTAXE TECHNIQUE EXACTE
    tools {
        hudson.plugins.sonar.SonarRunnerInstallation 'SonarScanner'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub.'
            }
        }

        stage('Install Dependencies') {
            steps {
                // Le chemin est correctement entre guillemets
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // On garde cette fonction qui prépare les variables d'environnement
                withSonarQubeEnv('sonarqube') { 
                    // Et on appelle le scanner. Grâce à la section 'tools', Jenkins saura où le trouver.
                    sh 'sonar-scanner' 
                }
            }
        }
    }

    post {
        always {
            echo 'Le pipeline est terminé.'
        }
    }
}
