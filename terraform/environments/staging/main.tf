terraform {
  backend "s3" {
    bucket = "aws-infra-terraform-staging-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

module "main" {
  source = "../../"
  
  environment = "staging"
  project     = "aws-infra"
  
  vpc_cidr           = "10.1.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  public_subnets     = ["10.1.1.0/24", "10.1.2.0/24"]
  private_subnets    = ["10.1.3.0/24", "10.1.4.0/24"]
  
  instance_type  = "t3.small"
  instance_count = 2
}
