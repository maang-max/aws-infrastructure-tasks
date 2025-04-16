stack {
  name = "prod"
  description = "Production environment infrastructure"
  
  before = [
    # Dependencies - typically prod would deploy after successful staging
    "/terraform/environments/staging"
  ]
  
  after = []
  
  # Define tags for this stack
  tags = ["prod", "aws"]
}
