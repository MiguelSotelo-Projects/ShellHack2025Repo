"""
Google ADK Configuration and Initialization

This module handles Google Cloud Platform configuration and initialization
for the agent system using Google's Application Development Kit.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from google.cloud import aiplatform
from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import logging as cloud_logging
from google.cloud import monitoring_v3
from google.auth import default
from google.oauth2 import service_account
import google.auth.exceptions


@dataclass
class GoogleADKConfig:
    """Google ADK configuration."""
    project_id: str
    region: str
    credentials_path: Optional[str] = None
    service_account_email: Optional[str] = None
    pubsub_topic_prefix: str = "ops-mesh"
    storage_bucket: Optional[str] = None
    ai_platform_endpoint: Optional[str] = None
    monitoring_enabled: bool = True
    logging_enabled: bool = True
    
    def __post_init__(self):
        if not self.storage_bucket:
            self.storage_bucket = f"{self.project_id}-ops-mesh-storage"


class GoogleADKManager:
    """Manages Google ADK initialization and configuration."""
    
    def __init__(self, config: GoogleADKConfig):
        self.config = config
        self.logger = logging.getLogger("google_adk")
        self.credentials = None
        self.clients = {}
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Google ADK services."""
        try:
            self.logger.info("Initializing Google ADK...")
            
            # Set up authentication
            await self._setup_authentication()
            
            # Initialize AI Platform
            await self._initialize_ai_platform()
            
            # Initialize Pub/Sub
            await self._initialize_pubsub()
            
            # Initialize Cloud Storage
            await self._initialize_storage()
            
            # Initialize Cloud Logging
            if self.config.logging_enabled:
                await self._initialize_logging()
            
            # Initialize Cloud Monitoring
            if self.config.monitoring_enabled:
                await self._initialize_monitoring()
            
            self.initialized = True
            self.logger.info("Google ADK initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google ADK: {e}")
            return False
    
    async def _setup_authentication(self):
        """Set up Google Cloud authentication."""
        try:
            if self.config.credentials_path and os.path.exists(self.config.credentials_path):
                # Use service account key file
                self.credentials = service_account.Credentials.from_service_account_file(
                    self.config.credentials_path
                )
                self.logger.info(f"Using service account credentials from {self.config.credentials_path}")
            else:
                # Use default credentials (ADC, environment, etc.)
                self.credentials, project = default()
                self.logger.info("Using default Google Cloud credentials")
            
            # Set environment variable for other Google Cloud libraries
            if self.credentials:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.credentials_path or ""
            
        except Exception as e:
            self.logger.error(f"Failed to setup authentication: {e}")
            raise
    
    async def _initialize_ai_platform(self):
        """Initialize AI Platform."""
        try:
            # Initialize AI Platform
            aiplatform.init(
                project=self.config.project_id,
                location=self.config.region,
                credentials=self.credentials
            )
            
            self.clients['aiplatform'] = aiplatform
            self.logger.info("AI Platform initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Platform: {e}")
            raise
    
    async def _initialize_pubsub(self):
        """Initialize Pub/Sub."""
        try:
            # Initialize Pub/Sub clients
            self.clients['publisher'] = pubsub_v1.PublisherClient(credentials=self.credentials)
            self.clients['subscriber'] = pubsub_v1.SubscriberClient(credentials=self.credentials)
            
            # Create default topics
            await self._create_default_topics()
            
            self.logger.info("Pub/Sub initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Pub/Sub: {e}")
            raise
    
    async def _create_default_topics(self):
        """Create default Pub/Sub topics."""
        try:
            topics_to_create = [
                f"{self.config.pubsub_topic_prefix}-agent-broadcast",
                f"{self.config.pubsub_topic_prefix}-orchestrator",
                f"{self.config.pubsub_topic_prefix}-frontdesk",
                f"{self.config.pubsub_topic_prefix}-scheduling",
                f"{self.config.pubsub_topic_prefix}-insurance",
                f"{self.config.pubsub_topic_prefix}-hospital",
                f"{self.config.pubsub_topic_prefix}-queue",
                f"{self.config.pubsub_topic_prefix}-staff"
            ]
            
            publisher = self.clients['publisher']
            
            for topic_name in topics_to_create:
                topic_path = publisher.topic_path(self.config.project_id, topic_name)
                try:
                    publisher.create_topic(request={"name": topic_path})
                    self.logger.info(f"Created topic: {topic_name}")
                except Exception:
                    # Topic might already exist
                    self.logger.debug(f"Topic {topic_name} already exists")
            
        except Exception as e:
            self.logger.error(f"Failed to create default topics: {e}")
            raise
    
    async def _initialize_storage(self):
        """Initialize Cloud Storage."""
        try:
            self.clients['storage'] = storage.Client(
                project=self.config.project_id,
                credentials=self.credentials
            )
            
            # Create default bucket if it doesn't exist
            await self._create_default_bucket()
            
            self.logger.info("Cloud Storage initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Cloud Storage: {e}")
            raise
    
    async def _create_default_bucket(self):
        """Create default storage bucket."""
        try:
            storage_client = self.clients['storage']
            bucket_name = self.config.storage_bucket
            
            try:
                bucket = storage_client.bucket(bucket_name)
                if not bucket.exists():
                    bucket = storage_client.create_bucket(bucket_name, location=self.config.region)
                    self.logger.info(f"Created bucket: {bucket_name}")
                else:
                    self.logger.info(f"Bucket {bucket_name} already exists")
            except Exception as e:
                self.logger.warning(f"Could not create bucket {bucket_name}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to create default bucket: {e}")
    
    async def _initialize_logging(self):
        """Initialize Cloud Logging."""
        try:
            self.clients['logging'] = cloud_logging.Client(
                project=self.config.project_id,
                credentials=self.credentials
            )
            
            self.logger.info("Cloud Logging initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Cloud Logging: {e}")
            raise
    
    async def _initialize_monitoring(self):
        """Initialize Cloud Monitoring."""
        try:
            self.clients['monitoring'] = monitoring_v3.MetricServiceClient(
                credentials=self.credentials
            )
            
            self.logger.info("Cloud Monitoring initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Cloud Monitoring: {e}")
            raise
    
    def get_client(self, service_name: str):
        """Get a Google Cloud client."""
        if not self.initialized:
            raise RuntimeError("Google ADK not initialized")
        
        if service_name not in self.clients:
            raise ValueError(f"Unknown service: {service_name}")
        
        return self.clients[service_name]
    
    def get_config(self) -> GoogleADKConfig:
        """Get the configuration."""
        return self.config
    
    def is_initialized(self) -> bool:
        """Check if Google ADK is initialized."""
        return self.initialized
    
    async def shutdown(self):
        """Shutdown Google ADK services."""
        try:
            # Close any open connections
            for service_name, client in self.clients.items():
                if hasattr(client, 'close'):
                    client.close()
            
            self.clients.clear()
            self.initialized = False
            
            self.logger.info("Google ADK shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during Google ADK shutdown: {e}")


def create_google_adk_config(
    project_id: Optional[str] = None,
    region: str = "us-central1",
    credentials_path: Optional[str] = None
) -> GoogleADKConfig:
    """Create Google ADK configuration from environment or parameters."""
    
    # Get project ID from environment or parameter
    if not project_id:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    
    if not project_id:
        raise ValueError("Google Cloud project ID must be provided or set in GOOGLE_CLOUD_PROJECT environment variable")
    
    # Get credentials path from environment or parameter
    if not credentials_path:
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    return GoogleADKConfig(
        project_id=project_id,
        region=region,
        credentials_path=credentials_path,
        pubsub_topic_prefix=os.getenv('OPS_MESH_TOPIC_PREFIX', 'ops-mesh'),
        monitoring_enabled=os.getenv('OPS_MESH_MONITORING', 'true').lower() == 'true',
        logging_enabled=os.getenv('OPS_MESH_LOGGING', 'true').lower() == 'true'
    )


# Global Google ADK manager instance
_google_adk_manager: Optional[GoogleADKManager] = None


async def initialize_google_adk(
    project_id: Optional[str] = None,
    region: str = "us-central1",
    credentials_path: Optional[str] = None
) -> GoogleADKManager:
    """Initialize the global Google ADK manager."""
    global _google_adk_manager
    
    if _google_adk_manager is None:
        config = create_google_adk_config(project_id, region, credentials_path)
        _google_adk_manager = GoogleADKManager(config)
        await _google_adk_manager.initialize()
    
    return _google_adk_manager


def get_google_adk_manager() -> GoogleADKManager:
    """Get the global Google ADK manager."""
    if _google_adk_manager is None:
        raise RuntimeError("Google ADK not initialized. Call initialize_google_adk() first.")
    
    return _google_adk_manager


async def shutdown_google_adk():
    """Shutdown the global Google ADK manager."""
    global _google_adk_manager
    
    if _google_adk_manager:
        await _google_adk_manager.shutdown()
        _google_adk_manager = None
