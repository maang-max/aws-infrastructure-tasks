stack {
  name = "dev"
  description = "Development environment infrastructure"
  
  before = [
    # Add any dependencies here if needed
  ]
  
  after = []
  
  # Define tags for this stack
  tags = ["dev", "aws"]
}
