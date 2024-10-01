import os
import boto3
import json
import urllib.request
from botocore.exceptions import ClientError

# Initialize AWS Clients
ec2_client = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')

# Environment Variables
TUNNEL1_IP = os.getenv('TUNNEL1_IP')
TUNNEL2_IP = os.getenv('TUNNEL2_IP')
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

def log_debug(message):
    if DEBUG:
        print(f"DEBUG: {message}")

def table_exists():
    """
    Check if the DynamoDB table exists.
    """
    try:
        dynamodb.meta.client.describe_table(TableName=DYNAMODB_TABLE_NAME)
        log_debug(f"Table '{DYNAMODB_TABLE_NAME}' exists.")
        return True
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        print(f"Table '{DYNAMODB_TABLE_NAME}' doesn't exist and creating...")
        return False

def create_dynamodb_table():
    if not table_exists():
        try:
            dynamodb.create_table(
                TableName=DYNAMODB_TABLE_NAME,
                KeySchema=[{'AttributeName': 'TunnelIP', 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': 'TunnelIP', 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            print(f"DynamoDB table '{DYNAMODB_TABLE_NAME}' created successfully.")
            # Wait for the table to be created before continuing
            dynamodb.meta.client.get_waiter('table_exists').wait(TableName=DYNAMODB_TABLE_NAME)
        except ClientError as e:
            print(f"Error creating DynamoDB table: {e}")

def get_vpn_status():
    response = ec2_client.describe_vpn_connections()
    vpn_connections = response.get('VpnConnections', [])
    
    vpn_status = {}
    for vpn in vpn_connections:
        for tunnel in vpn['VgwTelemetry']:
            outside_ip = tunnel['OutsideIpAddress']
            status = tunnel['Status']
            vpn_status[outside_ip] = status
            log_debug(f"Tunnel {outside_ip} status: {status}")
    
    return vpn_status

def send_alert(message):
    slack_payload = json.dumps({"text": message}).encode('utf-8')
    discord_payload = json.dumps({"content": message}).encode('utf-8')

    # Send to Slack if the SLACK_WEBHOOK is set
    if SLACK_WEBHOOK:
        try:
            if DEBUG:
                log_debug(f"Sending alert to Slack: {slack_payload.decode('utf-8')}")
            req = urllib.request.Request(SLACK_WEBHOOK, data=slack_payload, headers={'Content-Type': 'application/json'})
            response = urllib.request.urlopen(req)
            if DEBUG:
                log_debug(f"Slack response status: {response.status}, reason: {response.reason}")
                log_debug(f"Slack response body: {response.read().decode('utf-8')}")
            log_debug("Alert sent to Slack.")
        except Exception as e:
            log_debug(f"Error sending Slack alert: {e}")

    # Send to Discord if the DISCORD_WEBHOOK is set
    if DISCORD_WEBHOOK:
        try:
            if DEBUG:
                log_debug(f"Sending alert to Discord: {discord_payload.decode('utf-8')}")
            req = urllib.request.Request(DISCORD_WEBHOOK, data=discord_payload, headers={'Content-Type': 'application/json'})
            response = urllib.request.urlopen(req)
            if DEBUG:
                log_debug(f"Discord response status: {response.status}, reason: {response.reason}")
                log_debug(f"Discord response body: {response.read().decode('utf-8')}")
            log_debug("Alert sent to Discord.")
        except urllib.error.HTTPError as e:
            log_debug(f"Error sending Discord alert: {e}")
            error_body = e.read().decode('utf-8')
            log_debug(f"Discord error response body: {error_body}")

def update_status_in_dynamodb(tunnel_ip, status):
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    try:
        response = table.get_item(Key={'TunnelIP': tunnel_ip})
        if 'Item' in response:
            previous_status = response['Item']['Status']
            if previous_status != status:
                log_debug(f"Tunnel {tunnel_ip} status changed from {previous_status} to {status}.")
                send_alert(f"VPN Tunnel {tunnel_ip} status changed: {status}")
        else:
            log_debug(f"Adding new status for tunnel {tunnel_ip}: {status}")
            send_alert(f"VPN Tunnel {tunnel_ip} status is: {status}")
        
        # Update status in DynamoDB
        table.put_item(Item={'TunnelIP': tunnel_ip, 'Status': status})
    except ClientError as e:
        print(f"Error updating DynamoDB: {e}")

def monitor_vpn_tunnels():
    vpn_status = get_vpn_status()
    
    # Monitor Tunnel 1
    if TUNNEL1_IP and TUNNEL1_IP in vpn_status:
        update_status_in_dynamodb(TUNNEL1_IP, vpn_status[TUNNEL1_IP])
    
    # Monitor Tunnel 2 if set
    if TUNNEL2_IP and TUNNEL2_IP in vpn_status:
        update_status_in_dynamodb(TUNNEL2_IP, vpn_status[TUNNEL2_IP])

def lambda_handler(event, context):
    log_debug("Starting VPN Tunnel Monitoring...")
    create_dynamodb_table()
    monitor_vpn_tunnels()
    log_debug("Monitoring complete.")
