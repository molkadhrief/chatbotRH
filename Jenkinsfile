pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Code récupéré depuis GitHub.'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    
                    withCredentials([string(credentialsId: 'sonar-token-id', variable: 'SONAR_TOKEN

')]) {
                        withSonarQubeEnv('sonarqube') {
                            sh "${scannerHome}/bin/sonar-scanner"
                        }
                    }
                }
            }
        }
        
        stage('Quality Gate Check') {
            steps {
                script {
                    // CONTOURNEMENT : Vérification manuelle de la Quality Gate
                    // Cette étape remplace waitForQualityGate en utilisant le jeton injecté.
                    
                    // 1. Attendre que l'analyse soit traitée par SonarQube
                    sleep 15 // Attendre 15 secondes pour laisser le temps à SonarQube de traiter l'analyse
                    
                    // 2. Récupérer l'URL du rapport de l'analyse
                    def reportUrl = sh(script: 'grep "More about the report processing at" .scannerwork/report-task.txt | cut -d \' \' -f 6', returnStdout: true).trim()
                    
                    // 3. Interroger l'API de SonarQube pour obtenir le statut de la Quality Gate
                    def qualityGateStatus = sh(script: "curl -s -H \"Authorization: Bearer ${env.SONAR_TOKEN}\" ${reportUrl} | jq -r '.task.analysisId'", returnStdout: true).trim()
                    def analysisUrl = "${env.SONAR_HOST_URL}/api/qualitygates/project_status?analysisId=${qualityGateStatus}"
                    def gateResult = sh(script: "curl -s -H \"Authorization: Bearer ${env.SONAR_TOKEN}\" ${analysisUrl} | jq -r '.projectStatus.status'", returnStdout: true).trim()

                    if (gateResult == 'ERROR') {
                        error "La Quality Gate a échoué. Statut : ${gateResult}"
                    } else {
                        echo "La Quality Gate est passée. Statut : ${gateResult}"
                    }
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
