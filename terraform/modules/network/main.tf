resource "google_compute_network" "main" {
  name                    = "credit-scoring-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "main" {
  name          = "credit-scoring-subnet"
  ip_cidr_range = "10.10.0.0/20"
  region        = var.region
  network       = google_compute_network.main.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.20.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.30.0.0/20"
  }
}

locals {
  gke_node_tag = "credit-scoring-gke-node"
}

# Разрешаем обмен данными только внутри VPC и диапазонов Kubernetes.
resource "google_compute_firewall" "internal" {
  name    = "credit-scoring-allow-internal"
  network = google_compute_network.main.name

  direction = "INGRESS"
  priority  = 1000

  source_ranges = [
    "10.10.0.0/20",
    "10.20.0.0/16",
    "10.30.0.0/20",
  ]

  allow {
    protocol = "tcp"
  }

  allow {
    protocol = "udp"
  }

  allow {
    protocol = "icmp"
  }

  target_tags = [local.gke_node_tag]
}

# Диапазоны Google Load Balancer используются для health checks GKE Ingress.
resource "google_compute_firewall" "health_checks" {
  name    = "credit-scoring-allow-health-checks"
  network = google_compute_network.main.name

  direction = "INGRESS"
  priority  = 1000

  source_ranges = [
    "35.191.0.0/16",
    "130.211.0.0/22",
  ]

  allow {
    protocol = "tcp"
    ports    = ["30000-32767"]
  }

  target_tags = [local.gke_node_tag]
}




variable "region" {
  description = "Регион размещения подсети Google Cloud"
  type        = string
}

output "network_id" {
  description = "Идентификатор VPC"
  value       = google_compute_network.main.id
}

output "subnetwork_id" {
  description = "Идентификатор подсети"
  value       = google_compute_subnetwork.main.id
}

output "pods_range_name" {
  description = "Название диапазона IP-адресов Pod"
  value       = "pods"
}

output "services_range_name" {
  description = "Название диапазона IP-адресов Service"
  value       = "services"
}

output "gke_node_tag" {
  description = "Сетевой тег узлов GKE для применения firewall rules"
  value       = local.gke_node_tag
}
