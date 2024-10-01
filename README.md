# AWS Site-to-Site VPN Monitoring 🛡️

Stay on top of your AWS VPN connections with this automated monitoring solution! 🎯 This script is designed to monitor your AWS Site-to-Site VPN tunnels, sending out **real-time alerts** 🚨 via Slack and/or Discord while logging the connection status in DynamoDB 📊.

## 🌟 Features

- 🕵️ **Real-Time Monitoring**: Keep track of your VPN tunnel status with automatic checks.
- 💬 **Instant Notifications**: Receive alerts on Slack or Discord when something goes wrong.
- 📂 **DynamoDB Integration**: Store and update the connection status for future reference.
- 🛠️ **Debug Mode**: Easily toggle debug logs to see what's happening behind the scenes.

## 🔧 Requirements

To get started, make sure you have the following:

- ✅ AWS Lambda setup.
- ✅ AWS DynamoDB table for storing connection statuses.
- ✅ Slack or Discord webhooks for notifications.
- ✅ Appropriate IAM permissions (see below).

## 📜 IAM Policy

Don't forget to attach the following IAM policy to your Lambda execution role for permissions to interact with EC2 and DynamoDB:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVpnConnections"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:DescribeTable",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/*"
        }
    ]
}
```

## 🚀 Getting Started
### 1. Set up environment variables 🛠️

You'll need to configure the following environment variables in your Lambda function:

- TUNNEL1_IP – The IP address of VPN Tunnel 1 🌐
- TUNNEL2_IP – The IP address of VPN Tunnel 2 🌐
- SLACK_WEBHOOK – Slack Webhook URL for notifications 📩
- DISCORD_WEBHOOK – Discord Webhook URL for notifications 📩
- DYNAMODB_TABLE_NAME – The name of your DynamoDB table 🗂️
- DEBUG – Set to true to enable debug mode 🐛

### 2. Deploy to AWS Lambda 📡

Package and deploy the script to AWS Lambda using your preferred method (e.g., AWS SAM, Serverless Framework, etc.).

### 3. DynamoDB Table Setup 🔧

Ensure a DynamoDB table exists with the correct structure to store VPN statuses. The script will automatically create the table if it doesn't already exist.
🛠️ Usage

This script will periodically check the status of your VPN tunnels (both Tunnel 1 and Tunnel 2) 🕵️‍♂️. If any of the tunnels go down, you will be instantly notified via your configured Slack and/or Discord channels 🚨. Additionally, the connection status will be stored in DynamoDB 📊 for reference.
🔍 Debugging Mode

If you want to see detailed logs while the script runs, set the DEBUG environment variable to true. This will output helpful information for troubleshooting issues 🐛.
📈 How It Works

- Monitoring: The script uses AWS EC2's DescribeVpnConnections API to monitor VPN onnections in real-time.
- Notifications: If a tunnel goes down, the script sends notifications to Slack or iscord.
- DynamoDB Storage: The current status of the VPN connections is stored in a ynamoDB table for persistence.

## 🛡️ License

This project is licensed under the MIT License. See the LICENSE file for details.

Happy monitoring! 😎🎉