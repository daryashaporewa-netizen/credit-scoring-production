terraform {
  backend "gcs" {
    prefix = "credit-scoring/terraform/state"
  }
}

