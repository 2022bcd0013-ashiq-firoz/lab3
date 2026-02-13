pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        METRICS_FILE = "training-artifacts-py3.11/metrics.json"
        BEST_ACCURACY_FILE = "best-accuracy"
        DOCKER_IMAGE = "2022bcd0013ashiqfiroz/wine-quality-app-jenkins"
        CURRENT_ACCURACY = "0"
        MODEL_IMPROVED = "false"
        ARTIFACTS_DIR = "training-artifacts-py3.11"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/2022bcd0013-ashiq-firoz/lab3.git'
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                    python3 -m venv $VENV_DIR
                    . $VENV_DIR/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                    . $VENV_DIR/bin/activate
                    
                    # Create output directory for training script
                    mkdir -p output
                    
                    # Run training
                    python Script/train.py
                    
                    # Copy artifacts from output/ to training-artifacts-py3.11/
                    mkdir -p training-artifacts-py3.11
                    cp -r output/* training-artifacts-py3.11/
                    
                    # Verify copy was successful
                    echo "Contents of training-artifacts-py3.11/:"
                    ls -la training-artifacts-py3.11/
                '''
            }
        }

        stage('Archive Model Artifacts') {
            steps {
                script {
                    // Verify files exist before archiving
                    sh 'ls -la training-artifacts-py3.11/'
                    
                    // Archive the trained model files
                    archiveArtifacts artifacts: 'training-artifacts-py3.11/**/*', allowEmptyArchive: false
                    
                    // Stash for use in later stages
                    stash includes: 'training-artifacts-py3.11/**/*', name: 'model-artifacts'
                    
                    echo "Model artifacts archived successfully"
                }
            }
        }

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
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "false" }  // FIXED: Changed from "false"
            }
            steps {
                script {
                    // Unstash model artifacts before building
                    unstash 'model-artifacts'
                    
                    // Verify files are present
                    sh 'ls -la training-artifacts-py3.11/'
                    
                    docker.withRegistry('', 'dockerhub-creds') {
                        sh """
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                        docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${DOCKER_IMAGE}:latest
                        """
                    }
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "false" }  // FIXED: Changed from "false"
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