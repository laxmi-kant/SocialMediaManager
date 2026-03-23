variable "project_name" {
  type    = string
  default = "smm"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

# --- Networking ---
variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

# --- RDS ---
variable "db_instance_class" {
  type    = string
  default = "db.t3.small"
}

variable "db_multi_az" {
  type    = bool
  default = true
}

variable "db_backup_retention" {
  type    = number
  default = 30
}

# --- ElastiCache ---
variable "redis_node_type" {
  type    = string
  default = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  type    = number
  default = 2
}

# --- ECS ---
variable "image_tag" {
  type    = string
  default = "latest"
}

variable "backend_desired_count" {
  type    = number
  default = 2
}

variable "worker_desired_count" {
  type    = number
  default = 2
}

# --- Application ---
variable "frontend_url" {
  type    = string
  default = ""
}

variable "backend_url" {
  type    = string
  default = ""
}

variable "domain_name" {
  type    = string
  default = ""
}

variable "certificate_arn" {
  type    = string
  default = ""
}

# --- Monitoring ---
variable "alert_email" {
  type        = string
  description = "Email address for CloudWatch alarm notifications"
}
