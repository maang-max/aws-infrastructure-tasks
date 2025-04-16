# Terramate Cloud Integration Guide

This document provides instructions for setting up and using Terramate Cloud with this AWS infrastructure project.

## Prerequisites

1. A Terramate Cloud account (sign up at [cloud.terramate.io](https://cloud.terramate.io))
2. An organization created in Terramate Cloud
3. GitHub repository connected to Terramate Cloud

## Setup Instructions

### 1. Install the Terramate GitHub App

1. Go to your Terramate Cloud organization settings
2. Navigate to the Integrations section
3. Click on "GitHub App" and follow the installation instructions
4. Select the repository `aws-infra-terraform` during installation

### 2. Generate a Terramate Cloud API Token

1. Go to your Terramate Cloud user settings
2. Navigate to the API Tokens section
3. Create a new token with an appropriate description (e.g., "GitHub Actions")
4. Copy the token value

### 3. Add Required Secrets to GitHub Repository

Add the following secrets to your GitHub repository:

- `TERRAMATE_CLOUD_TOKEN`: The API token generated in step 2
- `AWS_ACCESS_KEY_ID`: AWS access key with appropriate permissions
- `AWS_SECRET_ACCESS_KEY`: Corresponding AWS secret key

### 4. Configure Environment Variables (Optional)

For local development, you can set the following environment variables:

```bash
export TM_CLOUD_ORGANIZATION=aws-infra-terraform
export TM_CLOUD_TOKEN=your_token_here
```

## Using Terramate Cloud

### Viewing Plans in Pull Requests

When a pull request is created or updated, the GitHub Actions workflow will:

1. Run Terramate to generate plans for changed stacks
2. Upload the plans to Terramate Cloud
3. Add a comment to the PR with a link to view the plans in Terramate Cloud

### Tracking Deployments

When changes are merged to the master branch, the GitHub Actions workflow will:

1. Apply the changes using Terramate
2. Record the deployment in Terramate Cloud
3. Update the deployment status when complete

### Accessing Terramate Cloud Dashboard

Visit [cloud.terramate.io](https://cloud.terramate.io) and navigate to your organization to:

- View all pull requests and their associated plans
- Track deployments and their status
- Monitor infrastructure changes over time
- Collaborate with team members on infrastructure changes

## Troubleshooting

If you encounter issues with Terramate Cloud integration:

1. Verify that the GitHub App is properly installed
2. Check that the API token is correctly configured in GitHub secrets
3. Ensure the `terramate.tm.hcl` file has the correct organization name
4. Review GitHub Actions workflow logs for any error messages
