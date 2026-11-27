variable "project_id" {
  description = "Идентификатор проекта Google Cloud"
  type        = string
}

variable "region" {
  description = "Регион размещения хранилища"
  type        = string
}

variable "bucket_name" {
  description = "Уникальное имя GCS-бакета"
  type        = string
}

resource "google_storage_bucket" "dvc" {
  name                        = var.bucket_name
  project                     = var.project_id
  location                    = var.region
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  public_access_prevention = "enforced"

  labels = {
    project = "credit-scoring"
    purpose = "dvc-artifacts"
  }
}

output "bucket_name" {
  description = "Имя бакета для хранения DVC-артефактов"
  value       = google_storage_bucket.dvc.name
}

output "bucket_url" {
  description = "Адрес хранилища DVC"
  value       = "gs://${google_storage_bucket.dvc.name}"
}