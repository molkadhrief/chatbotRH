pipeline {
    agent any // Exécute ce pipeline sur n'importe quel agent Jenkins disponible

    stages {
        stage('Checkout') {
            steps {
                // Cette étape est gérée automatiquement par Jenkins
                // car nous avons choisi "Pipeline script from SCM".
                echo 'Code récupéré depuis GitHub.'
            }
        }

        stage('Install Dependencies') {
            steps {
                // Exécute la commande pour installer les paquets listés dans requirements.txt
                // Le chemin est "moka miko/requirements.txt" car le fichier est dans un sous-dossier
                sh 'pip install -r "moka miko/requirements.txt"'
            }
        }

        stage('Run Tests (Placeholder)') {
            steps {
                // Ici, vous mettriez les commandes pour lancer vos tests
                // Par exemple : sh 'pytest'
                echo 'Étape de test - à implémenter.'
            }
        }
    }

    post {
        always {
            echo 'Le pipeline est terminé.'
        }
    }
}
