#!/usr/bin/env python3
"""
Google ADK Setup Script

This script helps set up Google Cloud Platform configuration for the ADK agent system.
"""

import os
import sys
import json
import subprocess
from pathlib import Path


def print_header():
    """Print setup header."""
    print("🚀 Google ADK Setup for Ops Mesh Backend")
    print("=" * 50)
    print()


def check_gcloud_cli():
    """Check if gcloud CLI is installed."""
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud CLI is installed")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ Google Cloud CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud CLI not found")
        return False


def get_current_project():
    """Get current Google Cloud project."""
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except:
        return None


def list_available_projects():
    """List available Google Cloud projects."""
    try:
        result = subprocess.run(['gcloud', 'projects', 'list', '--format=json'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            projects = json.loads(result.stdout)
            return projects
        return []
    except:
        return []


def enable_required_apis(project_id):
    """Enable required Google Cloud APIs."""
    apis = [
        'aiplatform.googleapis.com',
        'pubsub.googleapis.com',
        'storage.googleapis.com',
        'logging.googleapis.com',
        'monitoring.googleapis.com'
    ]
    
    print(f"🔧 Enabling required APIs for project: {project_id}")
    
    for api in apis:
        try:
            print(f"   Enabling {api}...")
            result = subprocess.run([
                'gcloud', 'services', 'enable', api, '--project', project_id
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {api} enabled")
            else:
                print(f"   ❌ Failed to enable {api}: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Error enabling {api}: {e}")


def create_service_account(project_id):
    """Create service account for the application."""
    service_account_name = "ops-mesh-agent"
    service_account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
    
    print(f"🔐 Creating service account: {service_account_email}")
    
    try:
        # Create service account
        result = subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'create', service_account_name,
            '--display-name', 'Ops Mesh Agent Service Account',
            '--description', 'Service account for Ops Mesh hospital operations system',
            '--project', project_id
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"   ✅ Service account created: {service_account_email}")
        else:
            if "already exists" in result.stderr:
                print(f"   ✅ Service account already exists: {service_account_email}")
            else:
                print(f"   ❌ Failed to create service account: {result.stderr}")
                return None
                
    except Exception as e:
        print(f"   ❌ Error creating service account: {e}")
        return None
    
    return service_account_email


def assign_roles(project_id, service_account_email):
    """Assign required roles to service account."""
    roles = [
        'roles/aiplatform.user',
        'roles/pubsub.admin',
        'roles/storage.admin',
        'roles/logging.logWriter',
        'roles/monitoring.metricWriter',
        'roles/monitoring.viewer'
    ]
    
    print(f"🔑 Assigning roles to service account...")
    
    for role in roles:
        try:
            result = subprocess.run([
                'gcloud', 'projects', 'add-iam-policy-binding', project_id,
                '--member', f'serviceAccount:{service_account_email}',
                '--role', role
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Assigned role: {role}")
            else:
                print(f"   ❌ Failed to assign role {role}: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Error assigning role {role}: {e}")


def create_service_account_key(project_id, service_account_email):
    """Create and download service account key."""
    key_file = f"ops-mesh-service-account-{project_id}.json"
    
    print(f"🔑 Creating service account key...")
    
    try:
        result = subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'keys', 'create', key_file,
            '--iam-account', service_account_email,
            '--project', project_id
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            key_path = os.path.abspath(key_file)
            print(f"   ✅ Service account key created: {key_path}")
            return key_path
        else:
            print(f"   ❌ Failed to create service account key: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error creating service account key: {e}")
        return None


def create_env_file(project_id, region, key_path):
    """Create .env file with configuration."""
    env_content = f"""# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT={project_id}
GOOGLE_CLOUD_REGION={region}
GOOGLE_APPLICATION_CREDENTIALS={key_path}

# Ops Mesh Configuration
OPS_MESH_TOPIC_PREFIX=ops-mesh
OPS_MESH_MONITORING=true
OPS_MESH_LOGGING=true

# Database Configuration
DATABASE_URL=sqlite:///./ops_mesh.db

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Ops Mesh Backend

# Development Settings
DEBUG=true
RELOAD=true
"""
    
    env_file = ".env"
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created configuration file: {env_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def test_configuration(project_id, key_path):
    """Test the Google Cloud configuration."""
    print("🧪 Testing Google Cloud configuration...")
    
    # Set environment variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
    os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
    
    try:
        # Test imports
        from google.cloud import pubsub_v1
        from google.cloud import storage
        from google.cloud import logging
        from google.cloud import monitoring_v3
        import google.cloud.aiplatform
        
        print("   ✅ Google Cloud libraries imported successfully")
        
        # Test authentication
        try:
            storage_client = storage.Client(project=project_id)
            buckets = list(storage_client.list_buckets())
            print("   ✅ Storage client authentication successful")
        except Exception as e:
            print(f"   ⚠️  Storage client test failed: {e}")
        
        try:
            publisher = pubsub_v1.PublisherClient()
            project_path = publisher.common_project_path(project_id)
            print("   ✅ Pub/Sub client authentication successful")
        except Exception as e:
            print(f"   ⚠️  Pub/Sub client test failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Missing Google Cloud libraries: {e}")
        print("   Please install: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False


def main():
    """Main setup function."""
    print_header()
    
    # Check gcloud CLI
    if not check_gcloud_cli():
        print("❌ Please install Google Cloud CLI first:")
        print("   https://cloud.google.com/sdk/docs/install")
        return False
    
    print()
    
    # Get or select project
    current_project = get_current_project()
    if current_project:
        print(f"📋 Current project: {current_project}")
        use_current = input("Use current project? (y/n): ").lower().strip()
        if use_current == 'y':
            project_id = current_project
        else:
            project_id = None
    else:
        project_id = None
    
    if not project_id:
        # List available projects
        projects = list_available_projects()
        if projects:
            print("\n📋 Available projects:")
            for i, project in enumerate(projects):
                print(f"   {i+1}. {project['projectId']} - {project.get('name', 'No name')}")
            
            try:
                choice = int(input("\nSelect project (number): ")) - 1
                if 0 <= choice < len(projects):
                    project_id = projects[choice]['projectId']
                else:
                    print("❌ Invalid selection")
                    return False
            except ValueError:
                print("❌ Invalid input")
                return False
        else:
            project_id = input("Enter Google Cloud project ID: ").strip()
            if not project_id:
                print("❌ Project ID is required")
                return False
    
    print(f"\n🎯 Selected project: {project_id}")
    
    # Get region
    region = input("Enter region (default: us-central1): ").strip() or "us-central1"
    
    print(f"🌍 Selected region: {region}")
    print()
    
    # Enable APIs
    enable_required_apis(project_id)
    print()
    
    # Create service account
    service_account_email = create_service_account(project_id)
    if not service_account_email:
        print("❌ Failed to create service account")
        return False
    print()
    
    # Assign roles
    assign_roles(project_id, service_account_email)
    print()
    
    # Create service account key
    key_path = create_service_account_key(project_id, service_account_email)
    if not key_path:
        print("❌ Failed to create service account key")
        return False
    print()
    
    # Create .env file
    if not create_env_file(project_id, region, key_path):
        print("❌ Failed to create configuration file")
        return False
    print()
    
    # Test configuration
    if test_configuration(project_id, key_path):
        print("\n🎉 Google ADK setup completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Review the .env file")
        print("   2. Start the agent system: python start_agents.py")
        print("   3. Or start the API server: python run.py")
        return True
    else:
        print("\n❌ Setup completed but configuration test failed")
        print("   Please check the error messages above")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
