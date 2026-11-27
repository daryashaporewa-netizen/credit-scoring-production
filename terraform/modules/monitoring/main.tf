variable "project_id" {
  description = "Идентификатор проекта Google Cloud"
  type        = string
}

variable "cluster_name" {
  description = "Название Kubernetes-кластера"
  type        = string
}

# Панель мониторинга Kubernetes
resource "google_monitoring_dashboard" "gke" {
  project = var.project_id

  dashboard_json = jsonencode({
    displayName = "Credit Scoring - Kubernetes"

    gridLayout = {
      columns = 1

      widgets = [
        {
          title = "Использование CPU контейнерами"

          xyChart = {
            dataSets = [
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"kubernetes.io/container/cpu/core_usage_time\" AND resource.type=\"k8s_container\" AND resource.label.cluster_name=\"${var.cluster_name}\""

                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                    }
                  }
                }

                plotType = "LINE"
              }
            ]
          }
        }
      ]
    }
  })
}

# Предупреждение о перезапусках контейнеров
resource "google_monitoring_alert_policy" "container_restarts" {
  project      = var.project_id
  display_name = "Credit Scoring - Container Restarts"
  combiner     = "OR"

  conditions {
    display_name = "Container restart detected"

    condition_threshold {
      filter = "metric.type=\"kubernetes.io/container/restart_count\" AND resource.type=\"k8s_container\" AND resource.label.cluster_name=\"${var.cluster_name}\""

      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "0s"

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_DELTA"
      }
    }
  }

  documentation {
    content   = "Проверить состояние Pod и журналы контейнеров Kubernetes."
    mime_type = "text/markdown"
  }
}

output "dashboard_id" {
  description = "Идентификатор панели мониторинга"
  value       = google_monitoring_dashboard.gke.id
}

output "alert_policy_id" {
  description = "Идентификатор правила предупреждений"
  value       = google_monitoring_alert_policy.container_restarts.id
}