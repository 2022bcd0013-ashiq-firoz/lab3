pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        METRICS_FILE = "app/artifacts/metrics.json"
        BEST_ACCURACY_FILE = "best-accuracy"
        DOCKER_IMAGE = "2022bcd0013ashiqfiroz/wine-quality-app-jenkins"
        CURRENT_ACCURACY = "0"
        MODEL_IMPROVED = "false"
    }

    stages {

        /* ----------------------------- */
        stage('Checkout') {
        /* ----------------------------- */
            steps {
                git branch: 'main',
                    url: 'https://github.com/2022bcd0013-ashiq-firoz/lab3.git'
            }
        }

        /* ------------------------------------------- */
        stage('Setup Python Virtual Environment') {
        /* ------------------------------------------- */
            steps {
                sh '''
                    python3 -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        /* ---------------------- */
        stage('Train Model') {
        /* ---------------------- */
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    mkdir -p app/artifacts
                    python Script/train.py
                '''
            }
        }

        /* ---------------------- */
        stage('Read Accuracy') {
            steps {
                script {

                    if (!fileExists(env.METRICS_FILE)) {
                        echo "WARNING: Metrics file not found. Setting accuracy to 0."
                        env.CURRENT_ACCURACY = "0"
                        return
                    }

                    def accuracy = sh(
                        script: "jq -r '.[-1].accuracy' ${METRICS_FILE} 2>/dev/null || echo 0",
                        returnStdout: true
                    ).trim()

                    if (!accuracy || accuracy == "null") {
                        echo "WARNING: Accuracy not found in metrics.json. Defaulting to 0."
                        accuracy = "0"
                    }

                    env.CURRENT_ACCURACY = accuracy
                    echo "Current Accuracy: ${env.CURRENT_ACCURACY}"
                }
            }
        }


        stage('Compare Accuracy') {
            steps {
                script {

                    float current = env.CURRENT_ACCURACY.toFloat()
                    float best = 0.0
                    boolean improved = false

                    if (!fileExists(env.BEST_ACCURACY_FILE)) {
                        echo "No baseline found. First run → promoting model."
                        improved = true
                    } else {
                        best = readFile(env.BEST_ACCURACY_FILE).trim().toFloat()
                        echo "Best Accuracy: ${best}"

                        if (current > best) {
                            improved = true
                            echo "Model Improved!"
                        } else {
                            echo "Model did NOT improve."
                        }
                    }

                    if (improved) {
                        writeFile file: env.BEST_ACCURACY_FILE, text: "${current}"
                        env.MODEL_IMPROVED = "true"
                    } else {
                        env.MODEL_IMPROVED = "false"
                    }

                    echo "MODEL_IMPROVED = ${env.MODEL_IMPROVED}"
                    env.MODEL_IMPROVED = "true"
                }
            }
        }


        /* ----------------------------------------- */
        stage('Build Docker Image') {
        /* ----------------------------------------- */
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                script {
                    docker.withRegistry('', 'dockerhub-creds') {
                        sh """
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                        """
                    }
                }
            }
        }

        /* ----------------------------------------- */
        stage('Push Docker Image') {
        /* ----------------------------------------- */
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                script {
                    docker.withRegistry('', 'dockerhub-creds') {
                        sh """
                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${DOCKER_IMAGE}:latest
                        """
                    }
                }
            }
        }
    }
}
