pipeline {
    agent {
        label 'api-tests'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '10'))
    }

    triggers {
        githubPush()
        pollSCM('H/5 * * * *')
    }

    environment {
        APP_REPO = 'https://github.com/Haohua-Sun/full-stack-fastapi-template.git'
        APP_DIR = 'full-stack-fastapi-template'
        COMPOSE_PROJECT_NAME = 'jenkins-fastapi-ci'
        BASE_URL = 'http://host.docker.internal:18000'
        ADMIN_EMAIL = 'admin@example.com'
        ADMIN_PASSWORD = 'ci-password'
        API_TEST_DATABASE_URL = 'postgresql+psycopg://postgres:postgres@host.docker.internal:15432/app'
        API_TEST_TIMEOUT = '20'
        DOCKER_BUILDKIT = '1'
        COMPOSE_DOCKER_CLI_BUILD = '1'
    }

    stages {
        stage('Checkout API test suite') {
            steps {
                checkout scm
            }
        }

        stage('Checkout FastAPI application') {
            steps {
                sh '''
                    rm -rf "$APP_DIR"
                    git clone "$APP_REPO" "$APP_DIR"
                '''
            }
        }

        stage('Create app environment') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        cat > .env <<'EOF'
PROJECT_NAME=FastAPI Jenkins CI
STACK_NAME=fastapi-jenkins-ci
DOMAIN=localhost
FRONTEND_HOST=http://localhost:5173
ENVIRONMENT=local
BACKEND_CORS_ORIGINS=http://localhost:5173
SECRET_KEY=jenkins-ci-secret-key-for-api-automation-tests
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=ci-password
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DOCKER_IMAGE_BACKEND=fastapi-jenkins-ci-backend
DOCKER_IMAGE_FRONTEND=fastapi-jenkins-ci-frontend
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
EMAILS_FROM_EMAIL=noreply@example.com
SENTRY_DSN=
EOF

                        cat > compose.jenkins.yml <<'EOF'
services:
  db:
    ports:
      - "15432:5432"

  backend:
    ports:
      - "18000:8000"

networks:
  traefik-public:
    external: false
EOF
                    '''
                }
            }
        }

        stage('Start FastAPI backend') {
            steps {
                dir("${APP_DIR}") {
                    sh '''
                        docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yml -f compose.jenkins.yml down -v --remove-orphans
                        docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yml -f compose.jenkins.yml up -d --wait backend
                        curl -fsS "$BASE_URL/api/v1/utils/health-check/"
                    '''
                }
            }
        }

        stage('Install test dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m ruff check tests utils
                '''
            }
        }

        stage('API tests') {
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    sh '''
                        . .venv/bin/activate
                        python -m pytest -v --junitxml=pytest-results.xml
                    '''
                }
            }
        }

        stage('Generate Allure report') {
            steps {
                sh '''
                    if [ -d allure-results ] && [ "$(find allure-results -type f | wc -l)" -gt 0 ]; then
                        allure generate allure-results -o allure-report --clean
                    fi
                '''
            }
        }
    }

    post {
        always {
            dir("${APP_DIR}") {
                sh 'docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yml -f compose.jenkins.yml logs db prestart backend || true'
                sh 'docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.yml -f compose.jenkins.yml down -v --remove-orphans || true'
            }

            junit testResults: 'pytest-results.xml', allowEmptyResults: true
            allure commandline: 'allure',
                includeProperties: false,
                jdk: '',
                resultPolicy: 'LEAVE_AS_IS',
                results: [[path: 'allure-results']]
            archiveArtifacts artifacts: 'pytest-results.xml,allure-results/**,allure-report/**', allowEmptyArchive: true
        }
    }
}
