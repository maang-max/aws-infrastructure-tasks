globals {
  # Global variables for all stacks
  terraform_version = "1.5.0"
  aws_region = "us-east-1"
  project = "aws-infra"
  
  # Tags to be applied to all resources
  tags = {
    ManagedBy = "Terramate"
    Project = "aws-infra-terraform"
  }
}
