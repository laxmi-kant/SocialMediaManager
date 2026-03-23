#!/usr/bin/env bash
set -euo pipefail

# Rollback ECS services to the previous task definition revision
# Usage: ./rollback.sh [cluster] [service...]
# Example: ./rollback.sh smm-production backend celery-worker

CLUSTER="${1:-smm-production}"
shift || true
SERVICES=("${@:-backend celery-worker celery-worker-comments celery-beat}")
REGION="${AWS_REGION:-us-east-1}"

if [ ${#SERVICES[@]} -eq 0 ]; then
  SERVICES=(backend celery-worker celery-worker-comments celery-beat)
fi

echo "Rolling back services on cluster: $CLUSTER"
echo "Services: ${SERVICES[*]}"
echo ""

rollback_service() {
  local service_name="${CLUSTER}-${1}"

  # Get current task definition
  CURRENT_TD=$(aws ecs describe-services \
    --cluster "$CLUSTER" \
    --services "$service_name" \
    --query 'services[0].taskDefinition' \
    --output text \
    --region "$REGION")

  if [ "$CURRENT_TD" = "None" ] || [ -z "$CURRENT_TD" ]; then
    echo "  ERROR: Service $service_name not found"
    return 1
  fi

  # Extract family and revision
  FAMILY=$(echo "$CURRENT_TD" | awk -F'/' '{print $NF}' | awk -F':' '{print $1}')
  CURRENT_REV=$(echo "$CURRENT_TD" | awk -F':' '{print $NF}')
  PREVIOUS_REV=$((CURRENT_REV - 1))

  if [ "$PREVIOUS_REV" -lt 1 ]; then
    echo "  ERROR: No previous revision available for $service_name"
    return 1
  fi

  PREVIOUS_TD="${FAMILY}:${PREVIOUS_REV}"

  echo "  Current:  $FAMILY:$CURRENT_REV"
  echo "  Rolling back to: $FAMILY:$PREVIOUS_REV"

  # Update service to use previous task definition
  aws ecs update-service \
    --cluster "$CLUSTER" \
    --service "$service_name" \
    --task-definition "$PREVIOUS_TD" \
    --force-new-deployment \
    --region "$REGION" \
    --output text \
    --query 'service.serviceName' > /dev/null

  echo "  Rollback initiated for $service_name"
}

for svc in "${SERVICES[@]}"; do
  echo "[$svc]"
  rollback_service "$svc"
  echo ""
done

echo "Waiting for backend service to stabilize..."
aws ecs wait services-stable \
  --cluster "$CLUSTER" \
  --services "${CLUSTER}-backend" \
  --region "$REGION"

echo "Rollback complete. Backend service is stable."
echo ""
echo "Verify with: curl https://<your-domain>/health"
