#!/bin/bash
# Genesis Engine - AWS Deploy Script
# Usage: ./deploy.sh [api|dashboard|all]

set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
PROJECT="genesis-engine"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_BASE="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

echo "=== Genesis Engine Deploy ==="
echo "Region:  ${REGION}"
echo "Account: ${ACCOUNT_ID}"
echo ""

# Login to ECR
aws ecr get-login-password --region ${REGION} | \
    docker login --username AWS --password-stdin ${ECR_BASE}

deploy_api() {
    echo ">> Building API image..."
    docker build -t ${PROJECT}-api ./genesis-engine

    echo ">> Tagging and pushing to ECR..."
    docker tag ${PROJECT}-api:latest ${ECR_BASE}/${PROJECT}-api:latest
    docker push ${ECR_BASE}/${PROJECT}-api:latest

    echo ">> Updating ECS service..."
    aws ecs update-service \
        --cluster ${PROJECT} \
        --service ${PROJECT}-api \
        --force-new-deployment \
        --region ${REGION}

    echo ">> API deployed!"
}

deploy_dashboard() {
    # Get ALB URL for API
    ALB_DNS=$(aws elbv2 describe-load-balancers \
        --names ${PROJECT} \
        --query 'LoadBalancers[0].DNSName' \
        --output text --region ${REGION})

    echo ">> Building Dashboard image..."
    docker build \
        --build-arg NEXT_PUBLIC_API_URL=http://${ALB_DNS} \
        -t ${PROJECT}-dashboard ./dashboard

    echo ">> Tagging and pushing to ECR..."
    docker tag ${PROJECT}-dashboard:latest ${ECR_BASE}/${PROJECT}-dashboard:latest
    docker push ${ECR_BASE}/${PROJECT}-dashboard:latest

    echo ">> Updating ECS service..."
    aws ecs update-service \
        --cluster ${PROJECT} \
        --service ${PROJECT}-dashboard \
        --force-new-deployment \
        --region ${REGION}

    echo ">> Dashboard deployed!"
    echo ">> URL: http://${ALB_DNS}"
}

case "${1:-all}" in
    api)
        deploy_api
        ;;
    dashboard)
        deploy_dashboard
        ;;
    all)
        deploy_api
        deploy_dashboard
        ;;
    *)
        echo "Usage: $0 [api|dashboard|all]"
        exit 1
        ;;
esac

echo ""
echo "=== Deploy complete ==="
