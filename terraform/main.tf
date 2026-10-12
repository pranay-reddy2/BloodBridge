data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  name = "${var.project}-${var.environment}"
  azs  = slice(data.aws_availability_zones.available.names, 0, 2)

  tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

# ---------------------------------------------------------------------------
# Network: 2 AZs x (public + private) subnets, one shared NAT gateway
#   public  10.42.0.0/24, 10.42.1.0/24    -> internet-facing load balancers
#   private 10.42.16.0/20, 10.42.32.0/20  -> worker nodes and pods (VPC CNI uses many IPs)
# ---------------------------------------------------------------------------
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.21"

  name = "${local.name}-vpc"
  cidr = var.vpc_cidr
  azs  = local.azs

  public_subnets  = [for i, _ in local.azs : cidrsubnet(var.vpc_cidr, 8, i)]
  private_subnets = [for i, _ in local.azs : cidrsubnet(var.vpc_cidr, 4, i + 1)]

  enable_nat_gateway   = true
  single_nat_gateway   = true # one NAT keeps the demo cheap; use one per AZ in production
  enable_dns_hostnames = true
  enable_dns_support   = true

  # These tags let Kubernetes place internet-facing / internal load balancers in the right subnets.
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }
}

# ---------------------------------------------------------------------------
# EKS control plane + one managed node group in the private subnets
# ---------------------------------------------------------------------------
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.29"

  cluster_name    = local.name
  cluster_version = var.kubernetes_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access       = true
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs

  # The IAM identity running `terraform apply` becomes cluster admin (EKS access entries).
  enable_cluster_creator_admin_permissions = true
  authentication_mode                      = "API"

  # Control plane audit/API logs to CloudWatch (kept short to limit cost).
  cluster_enabled_log_types              = ["api", "audit", "authenticator"]
  cloudwatch_log_group_retention_in_days = 7

  cluster_addons = {
    coredns                = {}
    kube-proxy             = {}
    eks-pod-identity-agent = {}
    vpc-cni = {
      before_compute = true
      # Turns on enforcement of Kubernetes NetworkPolicy objects (used by the Helm chart).
      configuration_values = jsonencode({ enableNetworkPolicy = "true" })
    }
    # Needed so the PostgreSQL PersistentVolumeClaim can be backed by an EBS gp3 volume.
    aws-ebs-csi-driver = {
      service_account_role_arn = module.ebs_csi_irsa.iam_role_arn
    }
  }

  eks_managed_node_groups = {
    default = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = var.node_instance_types
      capacity_type  = var.node_capacity_type

      min_size     = var.node_min_size
      desired_size = var.node_desired_size
      max_size     = var.node_max_size

      disk_size = 30
      labels = {
        workload = "general"
      }
    }
  }
}

# IAM role for the EBS CSI driver's service account (IRSA): it may create/attach EBS volumes, nothing else.
module "ebs_csi_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.55"

  role_name             = "${local.name}-ebs-csi"
  attach_ebs_csi_policy = true

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:ebs-csi-controller-sa"]
    }
  }
}
