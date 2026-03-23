output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "backend_service_name" {
  value = aws_ecs_service.backend.name
}

output "worker_service_name" {
  value = aws_ecs_service.celery_worker.name
}

output "comments_worker_service_name" {
  value = aws_ecs_service.celery_worker_comments.name
}

output "beat_service_name" {
  value = aws_ecs_service.celery_beat.name
}

output "migration_task_definition_arn" {
  value = aws_ecs_task_definition.migration.arn
}

output "backend_task_definition_family" {
  value = aws_ecs_task_definition.backend.family
}
