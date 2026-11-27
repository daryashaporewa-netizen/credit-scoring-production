terraform {
  required_version = ">= 1.17.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Общие параметры

variable "project_id" {
  description = "Идентификатор проекта Google Cloud"
  type        = string
}

variable "region" {
  description = "Регион размещения облачных ресурсов"
  type        = string
  default     = "europe-west1"
}

variable "enable_gpu" {
  description = "Включить GPU-пул Kubernetes"
  type        = bool
  default     = false
}

# Сеть VPC и подсети

module "network" {
  source = "./modules/network"

  region = var.region
}

# Kubernetes-кластер с CPU/GPU-пулами

module "kubernetes" {
  source = "./modules/kubernetes"

  project_id          = var.project_id
  region              = var.region
  network_id          = module.network.network_id
  subnetwork_id       = module.network.subnetwork_id
  pods_range_name     = module.network.pods_range_name
  services_range_name = module.network.services_range_name
  enable_gpu          = var.enable_gpu
}

# Хранилище артефактов DVC

module "storage" {
  source = "./modules/storage"

  project_id  = var.project_id
  region      = var.region
  bucket_name = "${var.project_id}-credit-scoring-dvc"
}

# Мониторинг Kubernetes

module "monitoring" {
  source = "./modules/monitoring"

  project_id   = var.project_id
  cluster_name = "credit-scoring-cluster"

  depends_on = [module.kubernetes]
}