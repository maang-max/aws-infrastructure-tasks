terraform {
  backend "s3" {
    bucket = "aws-infra-terraform-prod-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

module "main" {
  source = "../../"
  
  environment = "prod"
  project     = "aws-infra"
  
  vpc_cidr           = "10.2.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets     = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
  private_subnets    = ["10.2.4.0/24", "10.2.5.0/24", "10.2.6.0/24"]
  
  instance_type  = "t3.medium"
  instance_count = 3
}
