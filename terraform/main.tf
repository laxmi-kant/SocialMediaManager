# ============================================================
# Root Module - AI Social Media Manager AWS Infrastructure
# ============================================================

module "networking" {
  source = "./modules/networking"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

module "security" {
  source = "./modules/security"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.networking.vpc_id
}

module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
  environment  = var.environment
}

module "secrets" {
  source = "./modules/secrets"

  project_name = var.project_name
  environment  = var.environment
}

module "rds" {
  source = "./modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  private_subnet_ids = module.networking.private_subnet_ids
  security_group_id  = module.security.rds_sg_id
  instance_class     = var.db_instance_class
  multi_az           = var.db_multi_az
  backup_retention   = var.db_backup_retention
  master_password    = module.secrets.rds_password
}

module "elasticache" {
  source = "./modules/elasticache"

  project_name       = var.project_name
  environment        = var.environment
  private_subnet_ids = module.networking.private_subnet_ids
  security_group_id  = module.security.redis_sg_id
  node_type          = var.redis_node_type
  num_cache_nodes    = var.redis_num_cache_nodes
}

module "alb" {
  source = "./modules/alb"

  project_name      = var.project_name
  environment       = var.environment
  vpc_id            = module.networking.vpc_id
  public_subnet_ids = module.networking.public_subnet_ids
  security_group_id = module.security.alb_sg_id
  certificate_arn   = var.certificate_arn
}

module "ecs" {
  source = "./modules/ecs"

  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  private_subnet_ids    = module.networking.private_subnet_ids
  backend_sg_id         = module.security.backend_sg_id
  celery_sg_id          = module.security.celery_sg_id
  target_group_arn      = module.alb.target_group_arn
  ecr_repository_url    = module.ecr.repository_url
  app_config_secret_arn = module.secrets.app_config_secret_arn
  image_tag             = var.image_tag
  backend_desired_count = var.backend_desired_count
  worker_desired_count  = var.worker_desired_count
  frontend_url          = var.frontend_url != "" ? var.frontend_url : "https://${module.frontend.cloudfront_domain_name}"
  backend_url           = var.backend_url != "" ? var.backend_url : "http://${module.alb.alb_dns_name}"
}

module "frontend" {
  source = "./modules/frontend"

  project_name    = var.project_name
  environment     = var.environment
  certificate_arn = var.certificate_arn
  domain_name     = var.domain_name
}

module "monitoring" {
  source = "./modules/monitoring"

  project_name     = var.project_name
  environment      = var.environment
  ecs_cluster_name = module.ecs.cluster_name
  rds_instance_id  = "${var.project_name}-${var.environment}"
  alert_email      = var.alert_email
}
