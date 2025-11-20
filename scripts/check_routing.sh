#!/bin/bash

ALB_ARN=$(aws elbv2 describe-load-balancers --names vpbank-voice-agent-alb --query 'LoadBalancers[0].LoadBalancerArn' --output text)
LISTENER_ARN=$(aws elbv2 describe-listeners --load-balancer-arn "$ALB_ARN" --query 'Listeners[0].ListenerArn' --output text)

echo "=== ALB Listener Rules ==="
aws elbv2 describe-rules --listener-arn "$LISTENER_ARN" --output json | python3 -c "
import sys, json
rules = json.load(sys.stdin)['Rules']
for r in rules:
    priority = r['Priority']
    conditions = r.get('Conditions', [])
    if conditions and 'PathPatternConfig' in conditions[0]:
        paths = conditions[0]['PathPatternConfig']['Values']
        target = r['Actions'][0]['TargetGroupArn'].split('/')[-2] if 'TargetGroupArn' in r['Actions'][0] else 'N/A'
        print(f\"Priority: {priority}\")
        print(f\"Paths: {', '.join(paths)}\")
        print(f\"Target: {target}\")
        print()
    elif priority == 'default':
        target = r['Actions'][0]['TargetGroupArn'].split('/')[-2] if 'TargetGroupArn' in r['Actions'][0] else 'N/A'
        print(f\"Priority: {priority} (catches all other paths)\")
        print(f\"Target: {target}\")
        print()
"
