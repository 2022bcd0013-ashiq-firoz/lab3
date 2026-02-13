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


        /* -------------------------- */
        stage('Compare Accuracy') {
        /* -------------------------- */
            steps {
                script {

                    def bestAccuracy = "0"

                    if (fileExists(env.BEST_ACCURACY_FILE)) {
                        bestAccuracy = readFile(env.BEST_ACCURACY_FILE).trim()
                        echo "Existing Best Accuracy: ${bestAccuracy}"
                    } else {
                        echo "No baseline found. First run — auto-promoting model."
                        writeFile file: env.BEST_ACCURACY_FILE, text: env.CURRENT_ACCURACY
                        env.MODEL_IMPROVED = "true"
                        return
                    }

                    if (env.CURRENT_ACCURACY.toFloat() > bestAccuracy.toFloat()) {
                        echo "Model Improved!"
                        env.MODEL_IMPROVED = "true"
                        writeFile file: env.BEST_ACCURACY_FILE, text: env.CURRENT_ACCURACY
                    } else {
                        echo "Model did NOT improve."
                        env.MODEL_IMPROVED = "false"
                    }
                }
            }
        }

        /* ----------------------------------------- */
        stage('Build Docker Image (Conditional)') {
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
        stage('Push Docker Image (Conditional)') {
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
