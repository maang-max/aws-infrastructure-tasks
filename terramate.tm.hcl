terramate {
  required_version = ">= 0.13.0"
  
  config {
    git {
      default_branch = "master"
      default_remote = "origin"
    }
    
    cloud {
      organization = "cloudas"
      # Uncomment and set the location if needed
      # location = "eu" # or "us"
    }
  }
}
