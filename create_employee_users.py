#!/usr/bin/env python3
"""
Tạo các tài khoản employee cho VPBank Voice Assistant
- Role: employee (không thể tự đăng ký)
- Tài khoản được tạo sẵn bởi admin
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

# Danh sách employee accounts
EMPLOYEE_ACCOUNTS = [
    {
        'username': 'employee1',
        'email': 'employee1@vpbank.com',
        'password': 'Employee123!',
        'name': 'Nguyễn Văn A',
        'department': 'Customer Service'
    },
    {
        'username': 'employee2', 
        'email': 'employee2@vpbank.com',
        'password': 'Employee123!',
        'name': 'Trần Thị B',
        'department': 'Loan Department'
    },
    {
        'username': 'employee3',
        'email': 'employee3@vpbank.com', 
        'password': 'Employee123!',
        'name': 'Lê Văn C',
        'department': 'HR Department'
    },
    {
        'username': 'employee4',
        'email': 'employee4@vpbank.com',
        'password': 'Employee123!', 
        'name': 'Phạm Thị D',
        'department': 'Compliance'
    },
    {
        'username': 'employee5',
        'email': 'employee5@vpbank.com',
        'password': 'Employee123!',
        'name': 'Hoàng Văn E', 
        'department': 'Transaction Processing'
    }
]

def create_employee_user(user_data):
    """Tạo một employee user"""
    try:
        # Xóa user cũ nếu tồn tại
        try:
            cognito.admin_delete_user(
                UserPoolId=USER_POOL_ID,
                Username=user_data['username']
            )
            print(f"🗑️  Deleted existing user: {user_data['username']}")
        except ClientError as e:
            if e.response['Error']['Code'] != 'UserNotFoundException':
                print(f"⚠️  Warning deleting {user_data['username']}: {e}")
        
        # Tạo user mới với role employee (bỏ department vì chưa config trong Cognito)
        attributes = [
            {'Name': 'email', 'Value': user_data['email']},
            {'Name': 'email_verified', 'Value': 'true'},
            {'Name': 'name', 'Value': user_data['name']},
            {'Name': 'custom:role', 'Value': 'employee'}
            # Note: custom:department cần được config trong Cognito User Pool trước
        ]
        
        cognito.admin_create_user(
            UserPoolId=USER_POOL_ID,
            Username=user_data['username'],
            UserAttributes=attributes,
            TemporaryPassword='TempPass123!',
            MessageAction='SUPPRESS'
        )
        
        # Set permanent password
        cognito.admin_set_user_password(
            UserPoolId=USER_POOL_ID,
            Username=user_data['username'],
            Password=user_data['password'],
            Permanent=True
        )
        
        print(f"✅ Created employee: {user_data['username']} ({user_data['name']}) - {user_data['department']}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UsernameExistsException':
            print(f"⚠️  Employee {user_data['username']} already exists")
        else:
            print(f"❌ Error creating employee {user_data['username']}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error creating {user_data['username']}: {e}")
        return False

def main():
    print("🏢 Creating VPBank Employee Accounts...")
    print("=" * 60)
    
    if not USER_POOL_ID:
        print("❌ COGNITO_USER_POOL_ID not found in environment variables")
        return
    
    success_count = 0
    total_count = len(EMPLOYEE_ACCOUNTS)
    
    for employee in EMPLOYEE_ACCOUNTS:
        if create_employee_user(employee):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Employee Creation Complete!")
    print(f"✅ Successfully created: {success_count}/{total_count} employees")
    print("\n📋 Employee Login Credentials:")
    print("-" * 40)
    
    for employee in EMPLOYEE_ACCOUNTS:
        print(f"👤 {employee['name']} ({employee['department']})")
        print(f"   Username: {employee['username']}")
        print(f"   Password: {employee['password']}")
        print(f"   Email: {employee['email']}")
        print()
    
    print("🔐 Role: employee")
    print("🚫 Note: Employee accounts cannot be self-registered")
    print("=" * 60)

if __name__ == "__main__":
    main()