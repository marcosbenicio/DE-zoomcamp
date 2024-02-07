terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.14.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)       # load content of JSON file credentials.
  project     = var.project                 # ID of the Google Cloud project.
  region      = var.region                  # Region where resources will be deployed.
}

resource "google_storage_bucket" "demo-bucket" {
  name          = var.gcs_bucket_name        # needs to be unique name across all GCP
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1             # In days
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}