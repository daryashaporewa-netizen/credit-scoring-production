# Переменные Kubernetes-модуля

variable "project_id" {
  description = "Идентификатор проекта Google Cloud"
  type        = string
}

variable "region" {
  description = "Регион размещения Kubernetes-кластера"
  type        = string
}

variable "network_id" {
  description = "Идентификатор VPC"
  type        = string
}

variable "subnetwork_id" {
  description = "Идентификатор подсети"
  type        = string
}

variable "pods_range_name" {
  description = "Название вторичного IP-диапазона для Pod"
  type        = string
}

variable "services_range_name" {
  description = "Название вторичного IP-диапазона для Service"
  type        = string
}

variable "node_network_tag" {
  description = "Сетевой тег узлов GKE"
  type        = string
}

variable "enable_gpu" {
  description = "Создавать ли GPU-пул Kubernetes"
  type        = bool
  default     = false
}


# Сервисный аккаунт Kubernetes-узлов

resource "google_service_account" "gke_nodes" {
  project      = var.project_id
  account_id   = "credit-scoring-gke-nodes"
  display_name = "Credit Scoring GKE Nodes"
}

resource "google_project_iam_member" "gke_nodes" {
  project = var.project_id
  role    = "roles/container.defaultNodeServiceAccount"
  member  = "serviceAccount:${google_service_account.gke_nodes.email}"
}


# Kubernetes-кластер

resource "google_container_cluster" "main" {
  name     = "credit-scoring-cluster"
  location = var.region

  network    = var.network_id
  subnetwork = var.subnetwork_id

  remove_default_node_pool = true
  initial_node_count       = 1

  networking_mode = "VPC_NATIVE"

  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_range_name
    services_secondary_range_name = var.services_range_name
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  network_policy {
    enabled  = true
    provider = "CALICO"
  }

  addons_config {
    network_policy_config {
      disabled = false
    }
  }

  deletion_protection = false
}


# CPU Node Pool

resource "google_container_node_pool" "cpu" {
  name       = "cpu-pool"
  location   = var.region
  cluster    = google_container_cluster.main.name
  node_count = 1

  depends_on = [google_project_iam_member.gke_nodes]

  node_config {
    machine_type    = "e2-standard-2"
    disk_size_gb    = 30
    disk_type       = "pd-standard"
    service_account = google_service_account.gke_nodes.email
    tags            = [var.node_network_tag]

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}


# GPU Node Pool

resource "google_container_node_pool" "gpu" {
  count = var.enable_gpu ? 1 : 0

  name     = "gpu-pool"
  location = var.region
  cluster  = google_container_cluster.main.name

  initial_node_count = 0

  depends_on = [google_project_iam_member.gke_nodes]

  autoscaling {
    total_min_node_count = 0
    total_max_node_count = 1
  }

  node_config {
    machine_type    = "g2-standard-4"
    disk_size_gb    = 50
    disk_type       = "pd-balanced"
    service_account = google_service_account.gke_nodes.email
    tags            = [var.node_network_tag]

    guest_accelerator {
      type  = "nvidia-l4"
      count = 1

      gpu_driver_installation_config {
        gpu_driver_version = "DEFAULT"
      }
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}
