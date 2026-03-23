# Single JSON secret for cost efficiency ($0.40/month vs $5.20 for individual secrets)
resource "aws_secretsmanager_secret" "app_config" {
  name                    = "${var.project_name}/${var.environment}/app-config"
  description             = "Application configuration for ${var.project_name} ${var.environment}"
  recovery_window_in_days = 7

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Initial placeholder value - must be populated manually after terraform apply
resource "aws_secretsmanager_secret_version" "app_config" {
  secret_id = aws_secretsmanager_secret.app_config.id
  secret_string = jsonencode({
    DATABASE_URL         = "placeholder"
    DATABASE_URL_SYNC    = "placeholder"
    REDIS_URL            = "placeholder"
    SECRET_KEY           = "placeholder"
    ENCRYPTION_KEY       = "placeholder"
    ANTHROPIC_API_KEY    = "placeholder"
    TWITTER_CLIENT_ID    = ""
    TWITTER_CLIENT_SECRET = ""
    LINKEDIN_CLIENT_ID   = ""
    LINKEDIN_CLIENT_SECRET = ""
    REDDIT_CLIENT_ID     = ""
    REDDIT_CLIENT_SECRET = ""
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}

# RDS master password (separate for RDS managed rotation)
resource "aws_secretsmanager_secret" "rds_password" {
  name                    = "${var.project_name}/${var.environment}/rds-master-password"
  description             = "RDS master password for ${var.project_name} ${var.environment}"
  recovery_window_in_days = 7

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "random_password" "rds" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  secret_id     = aws_secretsmanager_secret.rds_password.id
  secret_string = random_password.rds.result
}
