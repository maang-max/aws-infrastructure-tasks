#!/usr/bin/env python3
# Monitoring script for EC2 instances and ALB

import boto3
import argparse
import time
from datetime import datetime, timedelta
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='AWS Monitoring Script')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--period', type=int, default=5, help='Monitoring period in minutes')
    parser.add_argument('--environment', default='dev', help='Environment (dev, staging, prod)')
    return parser.parse_args()

def get_ec2_instances(ec2_client, environment):
    instances = []
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Environment',
                'Values': [environment]
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    
    return instances

def get_load_balancers(elbv2_client, environment):
    load_balancers = []
    response = elbv2_client.describe_load_balancers()
    
    for lb in response['LoadBalancers']:
        # Get tags to check environment
        tags_response = elbv2_client.describe_tags(
            ResourceArns=[lb['LoadBalancerArn']]
        )
        
        for tag_description in tags_response['TagDescriptions']:
            for tag in tag_description['Tags']:
                if tag['Key'] == 'Environment' and tag['Value'] == environment:
                    load_balancers.append({
                        'Arn': lb['LoadBalancerArn'],
                        'Name': lb['LoadBalancerName'],
                        'DNSName': lb['DNSName']
                    })
                    break
    
    return load_balancers

def get_ec2_metrics(cloudwatch_client, instance_id, period_minutes):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=period_minutes)
    
    metrics = {
        'CPUUtilization': {
            'Namespace': 'AWS/EC2',
            'MetricName': 'CPUUtilization',
            'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}],
            'Statistics': ['Average', 'Maximum'],
            'Unit': 'Percent'
        },
        'NetworkIn': {
            'Namespace': 'AWS/EC2',
            'MetricName': 'NetworkIn',
            'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}],
            'Statistics': ['Average', 'Sum'],
            'Unit': 'Bytes'
        },
        'NetworkOut': {
            'Namespace': 'AWS/EC2',
            'MetricName': 'NetworkOut',
            'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}],
            'Statistics': ['Average', 'Sum'],
            'Unit': 'Bytes'
        },
        'DiskReadBytes': {
            'Namespace': 'AWS/EC2',
            'MetricName': 'DiskReadBytes',
            'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}],
            'Statistics': ['Average', 'Sum'],
            'Unit': 'Bytes'
        },
        'DiskWriteBytes': {
            'Namespace': 'AWS/EC2',
            'MetricName': 'DiskWriteBytes',
            'Dimensions': [{'Name': 'InstanceId', 'Value': instance_id}],
            'Statistics': ['Average', 'Sum'],
            'Unit': 'Bytes'
        }
    }
    
    results = {}
    
    for metric_name, metric_info in metrics.items():
        response = cloudwatch_client.get_metric_statistics(
            Namespace=metric_info['Namespace'],
            MetricName=metric_info['MetricName'],
            Dimensions=metric_info['Dimensions'],
            StartTime=start_time,
            EndTime=end_time,
            Period=60 * period_minutes,
            Statistics=metric_info['Statistics'],
            Unit=metric_info['Unit']
        )
        
        if len(response['Datapoints']) > 0:
            datapoint = response['Datapoints'][0]
            results[metric_name] = datapoint
        else:
            results[metric_name] = None
    
    return results

def get_alb_metrics(cloudwatch_client, load_balancer, period_minutes):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=period_minutes)
    
    metrics = {
        'RequestCount': {
            'Namespace': 'AWS/ApplicationELB',
            'MetricName': 'RequestCount',
            'Dimensions': [{'Name': 'LoadBalancer', 'Value': load_balancer['Arn'].split('/')[-1]}],
            'Statistics': ['Sum'],
            'Unit': 'Count'
        },
        'TargetResponseTime': {
            'Namespace': 'AWS/ApplicationELB',
            'MetricName': 'TargetResponseTime',
            'Dimensions': [{'Name': 'LoadBalancer', 'Value': load_balancer['Arn'].split('/')[-1]}],
            'Statistics': ['Average', 'p95', 'p99'],
            'Unit': 'Seconds'
        },
        'HTTPCode_Target_2XX_Count': {
            'Namespace': 'AWS/ApplicationELB',
            'MetricName': 'HTTPCode_Target_2XX_Count',
            'Dimensions': [{'Name': 'LoadBalancer', 'Value': load_balancer['Arn'].split('/')[-1]}],
            'Statistics': ['Sum'],
            'Unit': 'Count'
        },
        'HTTPCode_Target_4XX_Count': {
            'Namespace': 'AWS/ApplicationELB',
            'MetricName': 'HTTPCode_Target_4XX_Count',
            'Dimensions': [{'Name': 'LoadBalancer', 'Value': load_balancer['Arn'].split('/')[-1]}],
            'Statistics': ['Sum'],
            'Unit': 'Count'
        },
        'HTTPCode_Target_5XX_Count': {
            'Namespace': 'AWS/ApplicationELB',
            'MetricName': 'HTTPCode_Target_5XX_Count',
            'Dimensions': [{'Name': 'LoadBalancer', 'Value': load_balancer['Arn'].split('/')[-1]}],
            'Statistics': ['Sum'],
            'Unit': 'Count'
        }
    }
    
    results = {}
    
    for metric_name, metric_info in metrics.items():
        response = cloudwatch_client.get_metric_statistics(
            Namespace=metric_info['Namespace'],
            MetricName=metric_info['MetricName'],
            Dimensions=metric_info['Dimensions'],
            StartTime=start_time,
            EndTime=end_time,
            Period=60 * period_minutes,
            Statistics=metric_info['Statistics'],
            Unit=metric_info['Unit']
        )
        
        if len(response['Datapoints']) > 0:
            datapoint = response['Datapoints'][0]
            results[metric_name] = datapoint
        else:
            results[metric_name] = None
    
    return results

def print_ec2_metrics(instance_id, metrics):
    print(f"\nInstance: {instance_id}")
    print("-" * 50)
    
    if metrics['CPUUtilization']:
        print(f"CPU Utilization: {metrics['CPUUtilization']['Average']:.2f}% (Max: {metrics['CPUUtilization']['Maximum']:.2f}%)")
    else:
        print("CPU Utilization: No data")
    
    if metrics['NetworkIn'] and metrics['NetworkOut']:
        network_in_mb = metrics['NetworkIn']['Sum'] / (1024 * 1024)
        network_out_mb = metrics['NetworkOut']['Sum'] / (1024 * 1024)
        print(f"Network Traffic: In: {network_in_mb:.2f} MB, Out: {network_out_mb:.2f} MB")
    else:
        print("Network Traffic: No data")
    
    if metrics['DiskReadBytes'] and metrics['DiskWriteBytes']:
        disk_read_mb = metrics['DiskReadBytes']['Sum'] / (1024 * 1024)
        disk_write_mb = metrics['DiskWriteBytes']['Sum'] / (1024 * 1024)
        print(f"Disk I/O: Read: {disk_read_mb:.2f} MB, Write: {disk_write_mb:.2f} MB")
    else:
        print("Disk I/O: No data")

def print_alb_metrics(load_balancer, metrics):
    print(f"\nLoad Balancer: {load_balancer['Name']} ({load_balancer['DNSName']})")
    print("-" * 50)
    
    if metrics['RequestCount']:
        print(f"Request Count: {metrics['RequestCount']['Sum']:.0f}")
    else:
        print("Request Count: No data")
    
    if metrics['TargetResponseTime']:
        print(f"Response Time: Avg: {metrics['TargetResponseTime']['Average']*1000:.2f} ms")
    else:
        print("Response Time: No data")
    
    success_count = metrics['HTTPCode_Target_2XX_Count']['Sum'] if metrics['HTTPCode_Target_2XX_Count'] else 0
    client_error_count = metrics['HTTPCode_Target_4XX_Count']['Sum'] if metrics['HTTPCode_Target_4XX_Count'] else 0
    server_error_count = metrics['HTTPCode_Target_5XX_Count']['Sum'] if metrics['HTTPCode_Target_5XX_Count'] else 0
    
    total_count = success_count + client_error_count + server_error_count
    
    if total_count > 0:
        success_rate = (success_count / total_count) * 100
        print(f"HTTP Status: 2XX: {success_count:.0f} ({success_rate:.2f}%), 4XX: {client_error_count:.0f}, 5XX: {server_error_count:.0f}")
    else:
        print("HTTP Status: No data")

def main():
    args = parse_arguments()
    
    # Initialize AWS clients
    ec2_client = boto3.client('ec2', region_name=args.region)
    elbv2_client = boto3.client('elbv2', region_name=args.region)
    cloudwatch_client = boto3.client('cloudwatch', region_name=args.region)
    
    print(f"AWS Monitoring Report - {args.environment.upper()} Environment")
    print(f"Region: {args.region}")
    print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Period: Last {args.period} minutes")
    print("=" * 50)
    
    # Get EC2 instances
    instances = get_ec2_instances(ec2_client, args.environment)
    print(f"Found {len(instances)} EC2 instances")
    
    # Get Load Balancers
    load_balancers = get_load_balancers(elbv2_client, args.environment)
    print(f"Found {len(load_balancers)} Load Balancers")
    
    # Get and print EC2 metrics
    for instance_id in instances:
        metrics = get_ec2_metrics(cloudwatch_client, instance_id, args.period)
        print_ec2_metrics(instance_id, metrics)
    
    # Get and print ALB metrics
    for lb in load_balancers:
        metrics = get_alb_metrics(cloudwatch_client, lb, args.period)
        print_alb_metrics(lb, metrics)
    
    print("\nMonitoring completed successfully!")

if __name__ == "__main__":
    main()
