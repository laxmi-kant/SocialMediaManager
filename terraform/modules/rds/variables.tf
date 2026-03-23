variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "security_group_id" {
  type = string
}

variable "instance_class" {
  type    = string
  default = "db.t3.small"
}

variable "multi_az" {
  type    = bool
  default = true
}

variable "backup_retention" {
  type    = number
  default = 30
}

variable "master_password" {
  type      = string
  sensitive = true
}
