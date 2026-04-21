variable "aws_region" {
  description = "AWS region for resources"
  type        = string
}

variable "openai_api_key" {
  description = "OpenAI API key for the researcher agent"
  type        = string
  sensitive   = true
}

variable "alex_api_endpoint" {
  description = "Alex API endpoint from Part 3"
  type        = string
}

variable "alex_api_key" {
  description = "Alex API key from Part 3"
  type        = string
  sensitive   = true
}

variable "scheduler_enabled" {
  description = "Enable automated research scheduler"
  type        = bool
  default     = false
}

variable "openrouter_api_key" {
  description = "Openrouter api key for the researcher agent"
  type        = string
  sensitive   = true
}

variable "openrouter_base_url" {
  description = "Openrouter base url for the models"
  type        = string
  default     = "https://openrouter.ai/api/v1"
}

variable "openrouter_model" {
  description = "Default model to use with openrouter"
  type        = string
  default     = "openai/gpt-4o-mini-2024-07-18"
}