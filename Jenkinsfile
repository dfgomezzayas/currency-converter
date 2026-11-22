// Pipeline de integración continua del conversor de monedas.
// Etapas: checkout -> construcción -> pruebas unitarias -> despliegue -> pruebas de humo.
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    // Revisa el repositorio cada ~5 minutos (Jenkins local no recibe webhooks de GitHub)
    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        // Nombre de proyecto propio para no chocar con la app levantada a mano
        COMPOSE_PROJECT_NAME = "cc-ci-${env.BUILD_NUMBER}"
        // Puerto distinto de 8080 (frontend manual) y 8081 (Jenkins)
        FRONTEND_PORT = '8090'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Construcción de imágenes') {
            steps {
                sh 'docker compose build'
                sh 'docker image ls "${COMPOSE_PROJECT_NAME}-*"'
            }
        }

        stage('Pruebas unitarias') {
            steps {
                // Las pruebas corren dentro de la imagen de la API recién construida
                sh '''
                    mkdir -p reports
                    docker run --name "${COMPOSE_PROJECT_NAME}-tests" --user root \
                        "${COMPOSE_PROJECT_NAME}-api" \
                        sh -c "pip install -q --no-cache-dir -r requirements-dev.txt && pytest -v --junitxml=/tmp/junit.xml"
                '''
            }
            post {
                always {
                    sh '''
                        docker cp "${COMPOSE_PROJECT_NAME}-tests:/tmp/junit.xml" reports/junit.xml || true
                        docker rm -f "${COMPOSE_PROJECT_NAME}-tests" || true
                    '''
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('Despliegue') {
            steps {
                // --wait espera a que la API pase su healthcheck
                sh 'docker compose up -d --wait'
                sh 'docker compose ps'
            }
        }

        stage('Pruebas de humo') {
            steps {
                // Se ejecutan dentro del contenedor frontend: recorren nginx -> api
                sh '''
                    docker compose exec -T frontend wget -qO- http://localhost/api/health | grep '"ok"'
                    docker compose exec -T frontend wget -qO- "http://localhost/api/convert?de=USD&a=COP&valor=10.5" | tee convert.json
                    grep -q CONVERSION_OK convert.json
                    grep -q '"resultado": *"*42000' convert.json
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose logs --no-color > compose.log 2>&1 || true'
            archiveArtifacts artifacts: 'compose.log, convert.json', allowEmptyArchive: true
            sh 'docker compose down --rmi local --volumes --remove-orphans || true'
            cleanWs()
        }
        success {
            echo 'Pipeline exitoso: pruebas, construcción y despliegue verificados.'
        }
        failure {
            echo 'Pipeline fallido: revisar la etapa marcada en rojo y el reporte de pruebas.'
        }
    }
}
