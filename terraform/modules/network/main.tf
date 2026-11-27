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
