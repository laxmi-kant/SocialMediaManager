output "alb_dns_name" {
  description = "Backend ALB DNS name"
  value       = module.alb.alb_dns_name
}

output "cloudfront_domain" {
  description = "Frontend CloudFront domain"
  value       = module.frontend.cloudfront_domain_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for backend image"
  value       = module.ecr.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.ecs.cluster_name
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.elasticache.primary_endpoint
}

output "s3_frontend_bucket" {
  description = "S3 bucket for frontend static files"
  value       = module.frontend.s3_bucket_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for cache invalidation"
  value       = module.frontend.cloudfront_distribution_id
}

output "migration_task_definition" {
  description = "Migration task definition ARN for ECS run-task"
  value       = module.ecs.migration_task_definition_arn
}
