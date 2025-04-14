# Disaster Recovery Plan

## Overview

This document outlines the disaster recovery (DR) plan for the AWS infrastructure deployed using Terraform. The plan defines recovery objectives, procedures, and responsibilities to ensure business continuity in the event of a disaster.

## Recovery Objectives

### Recovery Time Objective (RTO)

The Recovery Time Objective (RTO) defines the maximum acceptable time to restore the system after a disaster:

- **Critical systems**: 1 hour
- **Non-critical systems**: 4 hours

### Recovery Point Objective (RPO)

The Recovery Point Objective (RPO) defines the maximum acceptable data loss in terms of time:

- **Critical systems**: 15 minutes
- **Non-critical systems**: 1 hour

## Backup Strategy

### EC2 Instances

- **AMI Backups**: Daily automated AMI creation for all EC2 instances
- **Retention Period**: 30 days
- **Backup Script**: `/scripts/backup.sh` is used to automate the backup process

### EBS Volumes

- **Snapshots**: Daily automated snapshots for all EBS volumes
- **Retention Period**: 30 days
- **Backup Script**: `/scripts/backup.sh` is used to automate the snapshot process

### Configuration Data

- **Terraform State**: Stored in an S3 bucket with versioning enabled
- **Infrastructure Code**: Stored in GitHub with version control

## Disaster Recovery Procedures

### Failover Process

1. **Detection**:
   - CloudWatch alarms will trigger notifications when instances become unhealthy
   - The ALB will automatically route traffic away from unhealthy instances

2. **Assessment**:
   - Determine the scope and severity of the disaster
   - Identify affected components and services
   - Estimate recovery time

3. **Recovery**:
   - For single instance failure:
     - The ALB will automatically route traffic to healthy instances
     - Auto Scaling Group will replace the failed instance
   
   - For Availability Zone failure:
     - Traffic will automatically route to instances in healthy AZs
     - Auto Scaling Group will launch new instances in healthy AZs
   
   - For Region failure:
     - Restore from AMI backups in the DR region
     - Update DNS to point to the DR environment

### Testing and Validation

1. **Regular Testing**:
   - Conduct failover tests quarterly
   - Simulate instance failures and validate ALB behavior
   - Test the restoration process from AMI backups and snapshots

2. **Documentation**:
   - Document test results and lessons learned
   - Update DR procedures based on test findings

## Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| Infrastructure Team | - Monitor system health<br>- Execute recovery procedures<br>- Maintain backup systems |
| DevOps Team | - Maintain automation scripts<br>- Update DR documentation<br>- Conduct DR testing |
| Management | - Declare disaster situations<br>- Communicate with stakeholders<br>- Approve recovery actions |

## Communication Plan

1. **Internal Communication**:
   - Use predefined communication channels (Slack, email, phone)
   - Regular status updates during recovery
   - Post-incident review meetings

2. **External Communication**:
   - Customer notifications through established channels
   - Regular status updates on service availability
   - Post-incident reports for affected customers

## Recovery Verification

After executing the recovery procedures, verify the following:

1. All EC2 instances are running and healthy
2. The ALB is distributing traffic correctly
3. All application functionality is working as expected
4. CloudWatch metrics show normal system behavior
5. Security groups and IAM policies are correctly applied

## Plan Maintenance

This disaster recovery plan should be reviewed and updated:

- Quarterly, as part of regular DR testing
- After significant infrastructure changes
- After any actual disaster recovery event
- When recovery objectives (RTO/RPO) change
