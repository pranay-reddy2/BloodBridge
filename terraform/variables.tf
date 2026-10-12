variable "aws_region" {
  description = "AWS region for every resource"
  type        = string
  default     = "ap-south-1"
}

variable "project" {
  description = "Name prefix for all resources"
  type        = string
  default     = "bloodbridge"
}

variable "environment" {
  description = "Environment tag (dev / prod)"
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Who to contact about these resources (added as a tag)"
  type        = string
  default     = "devops-capstone"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.42.0.0/16"
}

variable "kubernetes_version" {
  description = "EKS control plane version. Pick one in *standard* support (extended support costs ~6x more): aws eks describe-cluster-versions --query 'clusterVersions[?versionStatus==`STANDARD_SUPPORT`].clusterVersion'"
  type        = string
  default     = "1.34"
}

variable "node_instance_types" {
  description = "Instance types for the managed node group (t3.medium = 2 vCPU / 4 GiB)"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_capacity_type" {
  description = "ON_DEMAND or SPOT. SPOT is ~60-70% cheaper and fine for a capstone demo."
  type        = string
  default     = "ON_DEMAND"

  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.node_capacity_type)
    error_message = "node_capacity_type must be ON_DEMAND or SPOT."
  }
}

variable "node_min_size" {
  type    = number
  default = 2
}

variable "node_desired_size" {
  type    = number
  default = 2
}

variable "node_max_size" {
  type    = number
  default = 4
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "CIDRs allowed to reach the public Kubernetes API endpoint. Narrow this to your own IP (x.x.x.x/32)."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}
