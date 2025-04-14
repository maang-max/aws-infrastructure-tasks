terraform {
  backend "s3" {
    bucket = "aws-infra-terraform-dev-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

module "main" {
  source = "../../"
  
  environment = "dev"
  project     = "aws-infra"
  
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  public_subnets     = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets    = ["10.0.3.0/24", "10.0.4.0/24"]
  
  instance_type  = "t3.micro"
  instance_count = 2
}
