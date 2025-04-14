#!/bin/bash
# Backup script for EBS volumes and AMIs

# Set variables
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed 's/[a-z]$//')
DATE=$(date +%Y-%m-%d-%H-%M)
DESCRIPTION="Backup created on $DATE"

# Create AMI backup
echo "Creating AMI backup for instance $INSTANCE_ID..."
AMI_ID=$(aws ec2 create-image \
  --instance-id $INSTANCE_ID \
  --name "backup-$INSTANCE_ID-$DATE" \
  --description "$DESCRIPTION" \
  --no-reboot \
  --region $REGION \
  --output text)

echo "AMI created: $AMI_ID"

# Tag the AMI
aws ec2 create-tags \
  --resources $AMI_ID \
  --tags Key=Name,Value="backup-$INSTANCE_ID-$DATE" \
  --region $REGION

# Get all EBS volumes attached to the instance
VOLUMES=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query "Reservations[0].Instances[0].BlockDeviceMappings[*].Ebs.VolumeId" \
  --output text \
  --region $REGION)

# Create snapshots for each volume
for VOLUME_ID in $VOLUMES; do
  echo "Creating snapshot for volume $VOLUME_ID..."
  SNAPSHOT_ID=$(aws ec2 create-snapshot \
    --volume-id $VOLUME_ID \
    --description "Snapshot of $VOLUME_ID from $INSTANCE_ID on $DATE" \
    --region $REGION \
    --output text \
    --query SnapshotId)
  
  echo "Snapshot created: $SNAPSHOT_ID"
  
  # Tag the snapshot
  aws ec2 create-tags \
    --resources $SNAPSHOT_ID \
    --tags Key=Name,Value="snapshot-$VOLUME_ID-$DATE" \
    --region $REGION
done

echo "Backup completed successfully!"

# Clean up old backups (older than 30 days)
echo "Cleaning up old backups..."

# Find and deregister old AMIs
OLD_AMIS=$(aws ec2 describe-images \
  --owners self \
  --filters "Name=name,Values=backup-$INSTANCE_ID-*" \
  --query "Images[?CreationDate<='$(date -d '30 days ago' --iso-8601)T00:00:00.000Z'].ImageId" \
  --output text \
  --region $REGION)

for AMI_ID in $OLD_AMIS; do
  echo "Deregistering old AMI: $AMI_ID"
  aws ec2 deregister-image --image-id $AMI_ID --region $REGION
done

# Find and delete old snapshots
OLD_SNAPSHOTS=$(aws ec2 describe-snapshots \
  --owner-ids self \
  --filters "Name=description,Values=Snapshot of * from $INSTANCE_ID on *" \
  --query "Snapshots[?StartTime<='$(date -d '30 days ago' --iso-8601)T00:00:00.000Z'].SnapshotId" \
  --output text \
  --region $REGION)

for SNAPSHOT_ID in $OLD_SNAPSHOTS; do
  echo "Deleting old snapshot: $SNAPSHOT_ID"
  aws ec2 delete-snapshot --snapshot-id $SNAPSHOT_ID --region $REGION
done

echo "Cleanup completed successfully!"
