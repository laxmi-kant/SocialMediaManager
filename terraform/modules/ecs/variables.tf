variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "backend_sg_id" {
  type = string
}

variable "celery_sg_id" {
  type = string
}

variable "target_group_arn" {
  type = string
}

variable "ecr_repository_url" {
  type = string
}

variable "app_config_secret_arn" {
  type = string
}

variable "image_tag" {
  type    = string
  default = "latest"
}

# Backend
variable "backend_desired_count" {
  type    = number
  default = 2
}

variable "backend_cpu" {
  type    = number
  default = 512
}

variable "backend_memory" {
  type    = number
  default = 1024
}

# Celery worker
variable "worker_desired_count" {
  type    = number
  default = 2
}

variable "worker_cpu" {
  type    = number
  default = 512
}

variable "worker_memory" {
  type    = number
  default = 1024
}

# Comments worker
variable "comments_worker_cpu" {
  type    = number
  default = 256
}

variable "comments_worker_memory" {
  type    = number
  default = 512
}

# Beat
variable "beat_cpu" {
  type    = number
  default = 256
}

variable "beat_memory" {
  type    = number
  default = 512
}

# Non-secret environment variables
variable "frontend_url" {
  type    = string
  default = ""
}

variable "backend_url" {
  type    = string
  default = ""
}

variable "log_group_prefix" {
  type    = string
  default = "/ecs"
}
