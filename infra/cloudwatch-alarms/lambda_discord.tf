# Lambda function for Discord webhook integration

# Lambda execution role
resource "aws_iam_role" "discord_lambda_role" {
  count = var.discord_webhook_url != "" ? 1 : 0
  name  = "${var.project_name}-${var.environment}-discord-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda basic execution policy
resource "aws_iam_role_policy_attachment" "discord_lambda_basic" {
  count      = var.discord_webhook_url != "" ? 1 : 0
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.discord_lambda_role[0].name
}

# Lambda function code
locals {
  discord_lambda_code = <<-EOF
import json
import urllib3
import os

http = urllib3.PoolManager()

def lambda_handler(event, context):
    discord_webhook_url = os.environ['DISCORD_WEBHOOK_URL']

    # Parse SNS message
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])

    # Determine alert color based on alarm state
    color = 0xFF0000  # Red for ALARM
    if sns_message.get('NewStateValue') == 'OK':
        color = 0x00FF00  # Green for OK

    # Create Discord embed
    discord_message = {
        "username": "AWS CloudWatch",
        "avatar_url": "https://a0.awsstatic.com/libra-css/images/logos/aws_logo_smile_1200x630.png",
        "embeds": [{
            "title": f"🚨 {sns_message.get('AlarmName', 'Unknown Alarm')}",
            "description": sns_message.get('AlarmDescription', 'No description'),
            "color": color,
            "fields": [
                {
                    "name": "상태",
                    "value": sns_message.get('NewStateValue', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "이전 상태",
                    "value": sns_message.get('OldStateValue', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "리전",
                    "value": sns_message.get('Region', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "메트릭",
                    "value": sns_message.get('MetricName', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "네임스페이스",
                    "value": sns_message.get('Namespace', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "시간",
                    "value": sns_message.get('StateChangeTime', 'Unknown'),
                    "inline": True
                },
                {
                    "name": "사유",
                    "value": sns_message.get('NewStateReason', 'No reason provided'),
                    "inline": False
                }
            ],
            "footer": {
                "text": "${var.environment.upper()} Environment"
            }
        }]
    }

    # Send to Discord
    encoded_msg = json.dumps(discord_message).encode('utf-8')
    resp = http.request('POST', discord_webhook_url,
                       body=encoded_msg,
                       headers={'Content-Type': 'application/json'})

    return {
        'statusCode': resp.status,
        'body': resp.data.decode('utf-8')
    }
EOF
}

# Lambda function
resource "aws_lambda_function" "discord_webhook" {
  count         = var.discord_webhook_url != "" ? 1 : 0
  filename      = data.archive_file.discord_lambda_zip[0].output_path
  function_name = "${var.project_name}-${var.environment}-discord-webhook"
  role          = aws_iam_role.discord_lambda_role[0].arn
  handler       = "index.lambda_handler"
  runtime       = "python3.9"
  timeout       = 10

  environment {
    variables = {
      DISCORD_WEBHOOK_URL = var.discord_webhook_url
    }
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Create zip file for Lambda
data "archive_file" "discord_lambda_zip" {
  count       = var.discord_webhook_url != "" ? 1 : 0
  type        = "zip"
  output_path = "/tmp/discord_lambda.zip"

  source {
    content  = local.discord_lambda_code
    filename = "index.py"
  }
}

# Lambda permission for SNS
resource "aws_lambda_permission" "discord_sns_critical" {
  count         = var.discord_webhook_url != "" ? 1 : 0
  statement_id  = "AllowExecutionFromSNSCritical"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_webhook[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.critical_alerts.arn
}

resource "aws_lambda_permission" "discord_sns_warning" {
  count         = var.discord_webhook_url != "" ? 1 : 0
  statement_id  = "AllowExecutionFromSNSWarning"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.discord_webhook[0].function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.warning_alerts.arn
}

# SNS subscription to Lambda
resource "aws_sns_topic_subscription" "critical_discord" {
  count     = var.discord_webhook_url != "" ? 1 : 0
  topic_arn = aws_sns_topic.critical_alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.discord_webhook[0].arn
}

resource "aws_sns_topic_subscription" "warning_discord" {
  count     = var.discord_webhook_url != "" ? 1 : 0
  topic_arn = aws_sns_topic.warning_alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.discord_webhook[0].arn
}
