#!/usr/bin/env python3
"""
Liệt kê tất cả users trong Cognito theo role
"""
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

# AWS Cognito configuration
REGION = os.getenv("AWS_REGION", "ap-southeast-1")
USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")

# Initialize Cognito client
auth_access_key = os.getenv("AUTH_AWS_ACCESS_KEY_ID")
auth_secret_key = os.getenv("AUTH_AWS_SECRET_ACCESS_KEY")

if auth_access_key and auth_secret_key:
    cognito = boto3.client(
        'cognito-idp',
        region_name=REGION,
        aws_access_key_id=auth_access_key,
        aws_secret_access_key=auth_secret_key
    )
    print(f"🔐 Using AUTH credentials: {auth_access_key[:8]}...")
else:
    # Fallback to main AWS credentials
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    if aws_access_key and aws_secret_key:
        cognito = boto3.client(
            'cognito-idp',
            region_name=REGION,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        print(f"🔐 Using main AWS credentials: {aws_access_key[:8]}...")
    else:
        cognito = boto3.client('cognito-idp', region_name=REGION)
        print("⚠️  Using default AWS credentials")

def get_user_attribute(attributes, name):
    """Lấy giá trị attribute từ danh sách attributes"""
    for attr in attributes:
        if attr['Name'] == name:
            return attr['Value']
    return None

def list_all_users():
    """Liệt kê tất cả users và phân loại theo role"""
    try:
        users_by_role = {
            'user': [],
            'employee': [],
            'unknown': []
        }
        
        # Lấy tất cả users
        paginator = cognito.get_paginator('list_users')
        page_iterator = paginator.paginate(UserPoolId=USER_POOL_ID)
        
        total_users = 0
        
        for page in page_iterator:
            for user in page['Users']:
                total_users += 1
                
                # Lấy thông tin user
                username = user['Username']
                status = user['UserStatus']
                created = user['UserCreateDate'].strftime('%Y-%m-%d %H:%M:%S')
                
                # Lấy attributes
                attributes = user.get('Attributes', [])
                name = get_user_attribute(attributes, 'name') or username
                email = get_user_attribute(attributes, 'email') or 'N/A'
                role = get_user_attribute(attributes, 'custom:role') or 'unknown'
                department = get_user_attribute(attributes, 'custom:department')
                
                user_info = {
                    'username': username,
                    'name': name,
                    'email': email,
                    'role': role,
                    'department': department,
                    'status': status,
                    'created': created
                }
                
                # Phân loại theo role
                if role in users_by_role:
                    users_by_role[role].append(user_info)
                else:
                    users_by_role['unknown'].append(user_info)
        
        return users_by_role, total_users
        
    except ClientError as e:
        print(f"❌ Error listing users: {e}")
        return None, 0

def print_users_by_role(users_by_role, total_users):
    """In danh sách users theo role"""
    print("\n" + "=" * 80)
    print(f"📊 VPBank Cognito Users Summary (Total: {total_users})")
    print("=" * 80)
    
    for role, users in users_by_role.items():
        if not users:
            continue
            
        role_icon = {
            'user': '👤',
            'employee': '👔', 
            'unknown': '❓'
        }.get(role, '❓')
        
        print(f"\n{role_icon} {role.upper()} ROLE ({len(users)} users):")
        print("-" * 50)
        
        for user in users:
            print(f"  • {user['name']} (@{user['username']})")
            print(f"    Email: {user['email']}")
            if user['department']:
                print(f"    Department: {user['department']}")
            print(f"    Status: {user['status']} | Created: {user['created']}")
            print()
    
    print("=" * 80)

def main():
    print("🏢 VPBank Cognito User Management")
    
    if not USER_POOL_ID:
        print("❌ COGNITO_USER_POOL_ID not found in environment variables")
        return
    
    users_by_role, total_users = list_all_users()
    
    if users_by_role is not None:
        print_users_by_role(users_by_role, total_users)
        
        # Thống kê
        user_count = len(users_by_role.get('user', []))
        employee_count = len(users_by_role.get('employee', []))
        unknown_count = len(users_by_role.get('unknown', []))
        
        print(f"\n📈 Statistics:")
        print(f"   👤 Regular Users: {user_count}")
        print(f"   👔 Employees: {employee_count}")
        print(f"   ❓ Unknown Role: {unknown_count}")
        print(f"   📊 Total: {total_users}")
    else:
        print("❌ Failed to retrieve user list")

if __name__ == "__main__":
    main()