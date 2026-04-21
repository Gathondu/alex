variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

# Clerk validation happens in Lambda, not at API Gateway level
variable "clerk_jwks_url" {
  description = "Clerk JWKS URL for JWT validation in Lambda"
  type        = string
}

variable "clerk_issuer" {
  description = "Clerk issuer URL (kept for Lambda environment)"
  type        = string
  default     = ""  # Not actually used but kept for backwards compatibility
}

# API Lambda deployment package: local zip (Docker) vs S3 artifact (e.g. GitHub Actions uploads zip + hash)
variable "api_lambda_package_source" {
  description = "local = backend/api/api_lambda.zip on disk; s3 = zip + base64sha256 sidecar in api_lambda_packages bucket (CI upload then terraform apply)"
  type        = string
  default     = "local"

  validation {
    condition     = contains(["local", "s3"], var.api_lambda_package_source)
    error_message = "api_lambda_package_source must be \"local\" or \"s3\"."
  }
}

variable "api_lambda_s3_zip_key" {
  description = "Object key for the deployment zip when api_lambda_package_source is s3"
  type        = string
  default     = "deployments/api_lambda.zip"
}

variable "api_lambda_s3_hash_key" {
  description = "Object key for a single-line file: base64(sha256(zip)) identical to Terraform filebase64sha256()"
  type        = string
  default     = "deployments/api_lambda.base64sha256"
}