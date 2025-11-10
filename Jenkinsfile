pipeline {
    agent any
    stages {
        stage('Test Download') {
            steps {
                sh '''
                    curl -L -o test.zip "https://github.com/SonarSource/sonar-scanner-cli/releases/download/4.8.0.2856/sonar-scanner-cli-4.8.0.2856-linux.zip"
                    echo "Téléchargement réussi? Taille du fichier:"
                    ls -lh test.zip
                '''
            }
        }
    }
}