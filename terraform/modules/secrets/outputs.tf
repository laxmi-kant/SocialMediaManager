output "app_config_secret_arn" {
  value = aws_secretsmanager_secret.app_config.arn
}

output "rds_password_secret_arn" {
  value = aws_secretsmanager_secret.rds_password.arn
}

output "rds_password" {
  value     = random_password.rds.result
  sensitive = true
}
