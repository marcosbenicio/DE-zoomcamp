variable "credentials" {
  description = "Path to the JSON file credentials."
  default     = "./keys/credentials.json"
}

variable "project" {
  description = "default project name that Terraform will use"
  default     = "terraform-runner-412811"
}

variable "region" {
  description = "Sets the default region for the infrastructure deployment"
  default     = "southamerica-east1"
}

variable "location" {
  description = "Indicates the location for the resources. Often similar to or the same as the region."
  default     = "southamerica-east1"
}

variable "bq_dataset_name" {
  description = "Names the BigQuery Dataset"
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "Name of a Google Cloud Storage (GCS) bucket."
  default     = "terraform-runner-412811-bucket"
}

variable "gcs_storage_class" {
  description = "Determines the storage class of the GCS bucket"
  default     = "STANDARD"    # common values: STANDARD, NEARLINE, COLDLINE
}