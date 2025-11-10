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
                // Installation de jq pour l'étape Quality Gate Check
                sh 'sudo apt-get update && sudo apt-get install -y jq'
                sh 'pip3 install -r "moka miko/requirements.txt" --no-cache-dir'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    
                    withCredentials([string(credentialsId: 'sonar-token-id', variable: 'SONAR_TOKEN')]) {
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
                    withCredentials([string(credentialsId: 'sonar-token-id', variable: 'SONAR_TOKEN')]) {
                        
                        // Attendre que l'analyse soit traitée
                        sh 'sleep 15' 
                        
                        // Récupérer l'URL du rapport de l'analyse
                        def ceTaskUrl = "${env.SONAR_HOST_URL}/api/ce/task?id=${env.SONAR_TASKID}"
                        def gateStatus = sh(
                            script: "curl -s -H \"Authorization: Bearer ${env.SONAR_TOKEN}\" \"${ceTaskUrl}\" | jq -r '.task.analysisId'",
                            returnStdout: true
                        ).trim()
                        
                        // Vérifier le statut de la Quality Gate
                        def qualityGateUrl = "${env.SONAR_HOST_URL}/api/qualitygates/project_status?analysisId=${gateStatus}"
                        def status = sh(
                            script: "curl -s -H \"Authorization: Bearer ${env.SONAR_TOKEN}\" \"${qualityGateUrl}\" | jq -r '.projectStatus.status'",
                            returnStdout: true
                        ).trim()

                        if (status == 'ERROR' || status == 'FAILED') {
                            error "La Quality Gate a échoué. Statut : ${status}"
                        } else {
                            echo "La Quality Gate est passée. Statut : ${status}"
                        }
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
