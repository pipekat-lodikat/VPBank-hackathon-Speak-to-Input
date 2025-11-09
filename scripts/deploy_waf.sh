#!/bin/bash
# Deploy AWS WAF for VPBank Voice Agent
# Protects against malicious requests and attacks

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== AWS WAF Deployment ===${NC}"

ALB_ARN="arn:aws:elasticloadbalancing:us-east-1:590183822512:loadbalancer/app/vpbank-voice-agent-alb/21a2eda047609e0d"

# Check if WAF already exists
existing_waf=$(aws wafv2 list-web-acls --scope REGIONAL --region us-east-1 --query "WebACLs[?Name=='vpbank-voice-agent-waf'].ARN" --output text 2>/dev/null || echo "")

if [ -n "$existing_waf" ]; then
    echo -e "${YELLOW}WAF already exists: $existing_waf${NC}"
    WAF_ARN="$existing_waf"
else
    echo -e "${YELLOW}Creating new WAF WebACL...${NC}"

    # Create WAF with basic rules
    WAF_ARN=$(aws wafv2 create-web-acl \
        --name vpbank-voice-agent-waf \
        --scope REGIONAL \
        --default-action Allow={} \
        --description "WAF for VPBank Voice Agent - blocks malicious requests" \
        --rules '[
            {
                "Name": "BlockMaliciousPaths",
                "Priority": 1,
                "Statement": {
                    "OrStatement": {
                        "Statements": [
                            {
                                "ByteMatchStatement": {
                                    "SearchString": "/console/bea-helpsets",
                                    "FieldToMatch": {
                                        "UriPath": {}
                                    },
                                    "TextTransformations": [
                                        {
                                            "Priority": 0,
                                            "Type": "LOWERCASE"
                                        }
                                    ],
                                    "PositionalConstraint": "CONTAINS"
                                }
                            },
                            {
                                "ByteMatchStatement": {
                                    "SearchString": "/bsguest.cgi",
                                    "FieldToMatch": {
                                        "UriPath": {}
                                    },
                                    "TextTransformations": [
                                        {
                                            "Priority": 0,
                                            "Type": "LOWERCASE"
                                        }
                                    ],
                                    "PositionalConstraint": "CONTAINS"
                                }
                            },
                            {
                                "ByteMatchStatement": {
                                    "SearchString": "sendmail",
                                    "FieldToMatch": {
                                        "UriPath": {}
                                    },
                                    "TextTransformations": [
                                        {
                                            "Priority": 0,
                                            "Type": "LOWERCASE"
                                        }
                                    ],
                                    "PositionalConstraint": "CONTAINS"
                                }
                            }
                        ]
                    }
                },
                "Action": {
                    "Block": {
                        "CustomResponse": {
                            "ResponseCode": 403
                        }
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": true,
                    "CloudWatchMetricsEnabled": true,
                    "MetricName": "BlockMaliciousPaths"
                }
            },
            {
                "Name": "AWSManagedRulesCommonRuleSet",
                "Priority": 2,
                "Statement": {
                    "ManagedRuleGroupStatement": {
                        "VendorName": "AWS",
                        "Name": "AWSManagedRulesCommonRuleSet"
                    }
                },
                "OverrideAction": {
                    "None": {}
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": true,
                    "CloudWatchMetricsEnabled": true,
                    "MetricName": "AWSManagedRulesCommonRuleSet"
                }
            },
            {
                "Name": "RateLimitRule",
                "Priority": 3,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 2000,
                        "AggregateKeyType": "IP"
                    }
                },
                "Action": {
                    "Block": {
                        "CustomResponse": {
                            "ResponseCode": 429
                        }
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": true,
                    "CloudWatchMetricsEnabled": true,
                    "MetricName": "RateLimitRule"
                }
            }
        ]' \
        --visibility-config SampledRequestsEnabled=true,CloudWatchMetricsEnabled=true,MetricName=vpbank-voice-agent-waf \
        --region us-east-1 \
        --query 'Summary.ARN' \
        --output text)

    echo -e "${GREEN}✓ WAF WebACL created: $WAF_ARN${NC}"
fi

# Associate WAF with ALB
echo -e "${YELLOW}Associating WAF with ALB...${NC}"
aws wafv2 associate-web-acl \
    --web-acl-arn "$WAF_ARN" \
    --resource-arn "$ALB_ARN" \
    --region us-east-1 2>&1 || echo "WAF may already be associated"

echo -e "${GREEN}✓ WAF associated with ALB${NC}"

echo ""
echo -e "${BLUE}=== Deployment Complete ===${NC}"
echo -e "${GREEN}✓ WAF ARN: $WAF_ARN${NC}"
echo -e "${GREEN}✓ Protected Resource: $ALB_ARN${NC}"
echo ""
echo -e "${BLUE}View WAF at:${NC}"
echo "https://console.aws.amazon.com/wafv2/homev2/web-acl/vpbank-voice-agent-waf/overview?region=us-east-1"
