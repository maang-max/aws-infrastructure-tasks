stack {
  name = "staging"
  description = "Staging environment infrastructure"
  
  before = [
    # Add any dependencies here if needed
  ]
  
  after = []
  
  # Define tags for this stack
  tags = ["staging", "aws"]
}
