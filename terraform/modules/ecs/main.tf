locals {
  image = "${var.ecr_repository_url}:${var.image_tag}"

  common_secrets = [
    { name = "DATABASE_URL", valueFrom = "${var.app_config_secret_arn}:DATABASE_URL::" },
    { name = "DATABASE_URL_SYNC", valueFrom = "${var.app_config_secret_arn}:DATABASE_URL_SYNC::" },
    { name = "REDIS_URL", valueFrom = "${var.app_config_secret_arn}:REDIS_URL::" },
    { name = "SECRET_KEY", valueFrom = "${var.app_config_secret_arn}:SECRET_KEY::" },
    { name = "ENCRYPTION_KEY", valueFrom = "${var.app_config_secret_arn}:ENCRYPTION_KEY::" },
    { name = "ANTHROPIC_API_KEY", valueFrom = "${var.app_config_secret_arn}:ANTHROPIC_API_KEY::" },
    { name = "TWITTER_CLIENT_ID", valueFrom = "${var.app_config_secret_arn}:TWITTER_CLIENT_ID::" },
    { name = "TWITTER_CLIENT_SECRET", valueFrom = "${var.app_config_secret_arn}:TWITTER_CLIENT_SECRET::" },
    { name = "LINKEDIN_CLIENT_ID", valueFrom = "${var.app_config_secret_arn}:LINKEDIN_CLIENT_ID::" },
    { name = "LINKEDIN_CLIENT_SECRET", valueFrom = "${var.app_config_secret_arn}:LINKEDIN_CLIENT_SECRET::" },
    { name = "REDDIT_CLIENT_ID", valueFrom = "${var.app_config_secret_arn}:REDDIT_CLIENT_ID::" },
    { name = "REDDIT_CLIENT_SECRET", valueFrom = "${var.app_config_secret_arn}:REDDIT_CLIENT_SECRET::" },
  ]

  common_env = [
    { name = "ENV", value = "production" },
    { name = "FRONTEND_URL", value = var.frontend_url },
    { name = "BACKEND_URL", value = var.backend_url },
    { name = "CORS_ORIGINS", value = var.frontend_url },
    { name = "TWITTER_CALLBACK_URL", value = "${var.backend_url}/api/v1/platforms/twitter/callback" },
    { name = "LINKEDIN_CALLBACK_URL", value = "${var.backend_url}/api/v1/platforms/linkedin/callback" },
    { name = "ACCESS_TOKEN_EXPIRE_MINUTES", value = "15" },
    { name = "REFRESH_TOKEN_EXPIRE_DAYS", value = "7" },
  ]
}

# --- ECS Cluster ---
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
  }
}

# --- CloudWatch Log Groups ---
resource "aws_cloudwatch_log_group" "services" {
  for_each = toset(["backend", "celery-worker", "celery-worker-comments", "celery-beat", "migration"])

  name              = "${var.log_group_prefix}/${var.project_name}-${var.environment}-${each.key}"
  retention_in_days = 30

  tags = {
    Environment = var.environment
  }
}

# ============================================================
# Backend Task Definition + Service
# ============================================================
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-${var.environment}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "backend"
    image     = local.image
    essential = true

    command = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]

    environment = local.common_env
    secrets     = local.common_secrets

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 15
    }

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.services["backend"].name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])

  tags = {
    Environment = var.environment
  }
}

resource "aws_ecs_service" "backend" {
  name            = "${var.project_name}-${var.environment}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.backend_desired_count
  launch_type     = "FARGATE"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.backend_sg_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "backend"
    container_port   = 8000
  }

  tags = {
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}

# ============================================================
# Celery Worker Task Definition + Service
# ============================================================
resource "aws_ecs_task_definition" "celery_worker" {
  family                   = "${var.project_name}-${var.environment}-celery-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "celery-worker"
    image     = local.image
    essential = true

    command = ["celery", "-A", "app.tasks.celery_app", "worker", "-l", "info",
      "-Q", "research,generation,publishing,analytics,profile", "--concurrency", "4"]

    environment = local.common_env
    secrets     = local.common_secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.services["celery-worker"].name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])

  tags = {
    Environment = var.environment
  }
}

resource "aws_ecs_service" "celery_worker" {
  name            = "${var.project_name}-${var.environment}-celery-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_worker.arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.celery_sg_id]
    assign_public_ip = false
  }

  tags = {
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}

# ============================================================
# Celery Worker Comments Task Definition + Service
# ============================================================
resource "aws_ecs_task_definition" "celery_worker_comments" {
  family                   = "${var.project_name}-${var.environment}-celery-worker-comments"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.comments_worker_cpu
  memory                   = var.comments_worker_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "celery-worker-comments"
    image     = local.image
    essential = true

    command = ["celery", "-A", "app.tasks.celery_app", "worker", "-l", "info",
      "-Q", "comments", "--concurrency", "2"]

    environment = local.common_env
    secrets     = local.common_secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.services["celery-worker-comments"].name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])

  tags = {
    Environment = var.environment
  }
}

resource "aws_ecs_service" "celery_worker_comments" {
  name            = "${var.project_name}-${var.environment}-celery-worker-comments"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_worker_comments.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.celery_sg_id]
    assign_public_ip = false
  }

  tags = {
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}

# ============================================================
# Celery Beat Task Definition + Service
# ============================================================
resource "aws_ecs_task_definition" "celery_beat" {
  family                   = "${var.project_name}-${var.environment}-celery-beat"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.beat_cpu
  memory                   = var.beat_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "celery-beat"
    image     = local.image
    essential = true

    command = ["celery", "-A", "app.tasks.celery_app", "beat", "-l", "info"]

    environment = local.common_env
    secrets     = local.common_secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.services["celery-beat"].name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])

  tags = {
    Environment = var.environment
  }
}

resource "aws_ecs_service" "celery_beat" {
  name            = "${var.project_name}-${var.environment}-celery-beat"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.celery_beat.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  # CRITICAL: min 0%, max 100% prevents two beat instances running simultaneously
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.celery_sg_id]
    assign_public_ip = false
  }

  tags = {
    Environment = var.environment
  }

  lifecycle {
    ignore_changes = [task_definition]
  }
}

# ============================================================
# Migration Task Definition (one-off, not a service)
# ============================================================
resource "aws_ecs_task_definition" "migration" {
  family                   = "${var.project_name}-${var.environment}-migration"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "migration"
    image     = local.image
    essential = true

    command = ["alembic", "upgrade", "head"]

    environment = local.common_env
    secrets     = local.common_secrets

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.services["migration"].name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])

  tags = {
    Environment = var.environment
  }
}

# ============================================================
# Auto Scaling
# ============================================================
resource "aws_appautoscaling_target" "backend" {
  max_capacity       = 6
  min_capacity       = var.backend_desired_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "backend_cpu" {
  name               = "${var.project_name}-${var.environment}-backend-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.backend.resource_id
  scalable_dimension = aws_appautoscaling_target.backend.scalable_dimension
  service_namespace  = aws_appautoscaling_target.backend.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_target" "worker" {
  max_capacity       = 8
  min_capacity       = var.worker_desired_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.celery_worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "worker_cpu" {
  name               = "${var.project_name}-${var.environment}-worker-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.worker.resource_id
  scalable_dimension = aws_appautoscaling_target.worker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.worker.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
