pipeline {
    agent any

    environment {
        AWS_REGION      = 'us-east-1'
        ECR_REPO        = 'genai-app'
        CLUSTER_NAME    = 'genai-eks-cluster'
        K8S_NAMESPACE   = 'genai'
        APP_NAME        = 'genai-app'
        IMAGE_TAG       = "${BUILD_NUMBER}"
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Get AWS Account ID') {
            steps {
                script {
                    env.AWS_ACCOUNT_ID = sh(
                        script: "aws sts get-caller-identity --query Account --output text",
                        returnStdout: true
                    ).trim()

                    env.IMAGE_URI = "${env.AWS_ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com/${env.ECR_REPO}:${env.IMAGE_TAG}"
                    echo "Using image: ${env.IMAGE_URI}"
                }
            }
        }

        stage('Create ECR Repository If Missing') {
            steps {
                sh '''
                    aws ecr describe-repositories --repository-names "$ECR_REPO" --region "$AWS_REGION" >/dev/null 2>&1 || \
                    aws ecr create-repository --repository-name "$ECR_REPO" --region "$AWS_REGION"
                '''
            }
        }

        stage('ECR Login') {
            steps {
                sh '''
                    aws ecr get-login-password --region "$AWS_REGION" | \
                    docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t "$ECR_REPO:$IMAGE_TAG" .
                    docker tag "$ECR_REPO:$IMAGE_TAG" "$IMAGE_URI"
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                sh '''
                    docker push "$IMAGE_URI"
                '''
            }
        }

        stage('Configure kubectl') {
            steps {
                sh '''
                    aws eks update-kubeconfig --region "$AWS_REGION" --name "$CLUSTER_NAME"
                    kubectl get nodes
                '''
            }
        }

        stage('Create Namespace If Missing') {
            steps {
                sh '''
                    kubectl get namespace "$K8S_NAMESPACE" >/dev/null 2>&1 || kubectl create namespace "$K8S_NAMESPACE"
                '''
            }
        }

        stage('Deploy to EKS') {
            steps {
                sh '''
                    cp k8s/deployment.yaml k8s/deployment-rendered.yaml
                    sed -i "s|IMAGE_PLACEHOLDER|$IMAGE_URI|g" k8s/deployment-rendered.yaml

                    kubectl apply -f k8s/deployment-rendered.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl rollout status deployment/"$APP_NAME" -n "$K8S_NAMESPACE" --timeout=300s
                    kubectl get all -n "$K8S_NAMESPACE"
                '''
            }
        }
    }

    post {
        success {
            echo "Deployment completed successfully."
            sh 'kubectl get svc -n "$K8S_NAMESPACE" || true'
        }
        failure {
            echo "Pipeline failed."
        }
        always {
            sh '''
                rm -f k8s/deployment-rendered.yaml || true
                docker image prune -f || true
            '''
        }
    }
}