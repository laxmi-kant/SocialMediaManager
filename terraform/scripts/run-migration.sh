#!/usr/bin/env bash
set -euo pipefail

# Run Alembic database migration as an ECS one-off task
# Usage: ./run-migration.sh [cluster] [task-definition]

CLUSTER="${1:-smm-production}"
TASK_DEF="${2:-smm-production-migration}"
REGION="${AWS_REGION:-us-east-1}"

echo "Running migration on cluster: $CLUSTER"
echo "Task definition: $TASK_DEF"

# Get network configuration from the existing backend service
NETWORK_CONFIG=$(aws ecs describe-services \
  --cluster "$CLUSTER" \
  --services "${CLUSTER}-backend" \
  --query 'services[0].networkConfiguration' \
  --output json \
  --region "$REGION")

if [ "$NETWORK_CONFIG" = "null" ] || [ -z "$NETWORK_CONFIG" ]; then
  echo "ERROR: Could not retrieve network configuration from backend service"
  exit 1
fi

# Run the migration task
TASK_ARN=$(aws ecs run-task \
  --cluster "$CLUSTER" \
  --task-definition "$TASK_DEF" \
  --launch-type FARGATE \
  --network-configuration "$NETWORK_CONFIG" \
  --overrides '{
    "containerOverrides": [{
      "name": "migration",
      "command": ["alembic", "upgrade", "head"]
    }]
  }' \
  --query 'tasks[0].taskArn' \
  --output text \
  --region "$REGION")

if [ "$TASK_ARN" = "None" ] || [ -z "$TASK_ARN" ]; then
  echo "ERROR: Failed to start migration task"
  exit 1
fi

echo "Migration task started: $TASK_ARN"
echo "Waiting for task to complete..."

# Wait for task to finish
aws ecs wait tasks-stopped \
  --cluster "$CLUSTER" \
  --tasks "$TASK_ARN" \
  --region "$REGION"

# Check exit code
EXIT_CODE=$(aws ecs describe-tasks \
  --cluster "$CLUSTER" \
  --tasks "$TASK_ARN" \
  --query 'tasks[0].containers[0].exitCode' \
  --output text \
  --region "$REGION")

if [ "$EXIT_CODE" != "0" ]; then
  echo "ERROR: Migration failed with exit code: $EXIT_CODE"

  # Fetch logs for debugging
  TASK_ID=$(echo "$TASK_ARN" | awk -F'/' '{print $NF}')
  echo "Fetching logs..."
  aws logs get-log-events \
    --log-group-name "/ecs/${CLUSTER}-migration" \
    --log-stream-name "migration/migration/$TASK_ID" \
    --limit 50 \
    --query 'events[].message' \
    --output text \
    --region "$REGION" 2>/dev/null || echo "(Could not retrieve logs)"

  exit 1
fi

echo "Migration completed successfully"
