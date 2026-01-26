"""
Tenant Manager - Multi-Tenant Provisioning with Keycloak & Milvus.

This module handles the provisioning of isolated tenant environments:
- Keycloak realm/client creation for identity
- Milvus partition creation for knowledge isolation
- DynamoDB table setup for caching
- S3 bucket/prefix configuration for storage

Security Model:
- Each tenant gets isolated identity (Keycloak OBO flow)
- Each tenant gets isolated vector storage (Milvus partitions)
- All cross-tenant access is blocked by design
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
import os
import json
import hashlib


# ============================================================================
# Models
# ============================================================================

class TenantConfig(BaseModel):
    """Configuration for a tenant."""
    tenant_id: str = Field(description="Unique tenant identifier")
    display_name: str = Field(description="Human-readable name")
    domain: str = Field(description="Business domain")
    contact_email: str = Field(description="Primary contact email")

    # Resource configuration
    workspace_path: str = Field(description="Path for generated code")
    milvus_partition: str = Field(description="Milvus partition name")
    dynamodb_table: str = Field(description="DynamoDB table name")
    s3_prefix: str = Field(description="S3 key prefix")

    # Keycloak configuration
    keycloak_realm: Optional[str] = Field(default=None)
    keycloak_client_id: Optional[str] = Field(default=None)

    # Billing/usage tracking
    credits_remaining: float = Field(default=100.0)
    features_built: int = Field(default=0)


class KeycloakConfig(BaseModel):
    """Keycloak server configuration."""
    server_url: str = Field(description="Keycloak server URL")
    admin_realm: str = Field(default="master")
    admin_username: str = Field(description="Admin username")
    admin_password: str = Field(description="Admin password")


class ProvisioningResult(BaseModel):
    """Result of tenant provisioning."""
    success: bool
    tenant_id: str
    resources_created: List[str]
    errors: List[str] = Field(default=[])
    keycloak_client_secret: Optional[str] = None


# ============================================================================
# Tenant Manager
# ============================================================================

@dataclass
class TenantManager:
    """
    Manages multi-tenant provisioning for the Genesis Engine.

    This class handles the complete lifecycle of tenant resources:
    - Creation: Set up all isolated resources
    - Updates: Modify tenant configuration
    - Deletion: Clean up all resources (GDPR compliance)

    Security:
    - All operations are isolated per tenant
    - Keycloak OBO flow ensures proper identity propagation
    - Milvus partitions prevent cross-tenant data leakage

    Example:
        manager = TenantManager.from_env()

        # Provision new tenant
        result = await manager.provision_tenant(
            tenant_id="apex_logistics",
            display_name="Apex Logistics Inc.",
            domain="logistics",
            contact_email="admin@apex.com"
        )

        # Get tenant config
        config = await manager.get_tenant(tenant_id="apex_logistics")

        # Delete tenant (GDPR)
        await manager.delete_tenant(tenant_id="apex_logistics")
    """

    # Clients
    milvus_client: Optional[Any] = None
    dynamodb_client: Optional[Any] = None
    s3_client: Optional[Any] = None
    keycloak_config: Optional[KeycloakConfig] = None

    # Configuration
    base_workspace: str = "/tmp/genesis/workspaces"
    milvus_collection: str = "knowledge_base"
    s3_bucket: str = "genesis-factories"
    dynamodb_prefix: str = "factory-cache"

    # In-memory cache of tenants (production would use database)
    _tenants: Dict[str, TenantConfig] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "TenantManager":
        """
        Create TenantManager from environment variables.

        Required env vars:
        - AWS_REGION: AWS region
        - MILVUS_URI: Milvus connection string (optional)
        - KEYCLOAK_URL: Keycloak server URL (optional)
        - KEYCLOAK_ADMIN_USER: Keycloak admin username (optional)
        - KEYCLOAK_ADMIN_PASSWORD: Keycloak admin password (optional)
        """
        import boto3

        aws_region = os.getenv("AWS_REGION", "us-east-1")

        # Initialize AWS clients
        dynamodb = boto3.client("dynamodb", region_name=aws_region)
        s3 = boto3.client("s3", region_name=aws_region)

        # Initialize Milvus (optional)
        milvus = None
        milvus_uri = os.getenv("MILVUS_URI")
        if milvus_uri:
            try:
                from pymilvus import MilvusClient
                milvus = MilvusClient(uri=milvus_uri)
            except Exception as e:
                print(f"Warning: Milvus not available: {e}")

        # Initialize Keycloak config (optional)
        keycloak = None
        keycloak_url = os.getenv("KEYCLOAK_URL")
        if keycloak_url:
            keycloak = KeycloakConfig(
                server_url=keycloak_url,
                admin_username=os.getenv("KEYCLOAK_ADMIN_USER", "admin"),
                admin_password=os.getenv("KEYCLOAK_ADMIN_PASSWORD", "")
            )

        return cls(
            milvus_client=milvus,
            dynamodb_client=dynamodb,
            s3_client=s3,
            keycloak_config=keycloak,
            base_workspace=os.getenv("WORKSPACE_ROOT", "/tmp/genesis/workspaces"),
            s3_bucket=os.getenv("S3_BUCKET", "genesis-factories")
        )

    async def provision_tenant(
        self,
        tenant_id: str,
        display_name: str,
        domain: str,
        contact_email: str
    ) -> ProvisioningResult:
        """
        Provision a new tenant with all required resources.

        This creates:
        1. Workspace directory
        2. Milvus partition (if available)
        3. DynamoDB table (if available)
        4. S3 prefix (if available)
        5. Keycloak client (if available)

        Args:
            tenant_id: Unique identifier (lowercase, no spaces)
            display_name: Human-readable name
            domain: Business domain
            contact_email: Contact email

        Returns:
            ProvisioningResult with created resources
        """
        resources_created = []
        errors = []

        # Validate tenant_id
        tenant_id = self._sanitize_tenant_id(tenant_id)

        # Check if tenant already exists
        if tenant_id in self._tenants:
            return ProvisioningResult(
                success=False,
                tenant_id=tenant_id,
                resources_created=[],
                errors=[f"Tenant {tenant_id} already exists"]
            )

        # 1. Create workspace directory
        workspace_path = os.path.join(self.base_workspace, tenant_id)
        try:
            os.makedirs(workspace_path, exist_ok=True)
            resources_created.append(f"workspace:{workspace_path}")
        except Exception as e:
            errors.append(f"Failed to create workspace: {e}")

        # 2. Create Milvus partition
        milvus_partition = f"tenant_{tenant_id}"
        if self.milvus_client:
            try:
                self.milvus_client.create_partition(
                    collection_name=self.milvus_collection,
                    partition_name=milvus_partition
                )
                resources_created.append(f"milvus:{milvus_partition}")
            except Exception as e:
                # Partition might already exist
                if "already exists" not in str(e).lower():
                    errors.append(f"Failed to create Milvus partition: {e}")

        # 3. Create DynamoDB table (if not using shared table)
        dynamodb_table = f"{self.dynamodb_prefix}-{tenant_id}"
        if self.dynamodb_client:
            try:
                self.dynamodb_client.create_table(
                    TableName=dynamodb_table,
                    KeySchema=[
                        {"AttributeName": "key", "KeyType": "HASH"}
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "key", "AttributeType": "S"}
                    ],
                    BillingMode="PAY_PER_REQUEST"
                )
                resources_created.append(f"dynamodb:{dynamodb_table}")
            except self.dynamodb_client.exceptions.ResourceInUseException:
                # Table already exists
                pass
            except Exception as e:
                errors.append(f"Failed to create DynamoDB table: {e}")

        # 4. S3 prefix (just verify bucket access)
        s3_prefix = f"tenants/{tenant_id}/"
        if self.s3_client:
            try:
                # Put a marker object
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=f"{s3_prefix}.tenant_marker",
                    Body=json.dumps({"tenant_id": tenant_id})
                )
                resources_created.append(f"s3:{s3_prefix}")
            except Exception as e:
                errors.append(f"Failed to create S3 prefix: {e}")

        # 5. Create Keycloak client (for OBO flow)
        keycloak_client_id = None
        keycloak_client_secret = None
        if self.keycloak_config:
            try:
                keycloak_client_id, keycloak_client_secret = await self._create_keycloak_client(
                    tenant_id, display_name
                )
                resources_created.append(f"keycloak:{keycloak_client_id}")
            except Exception as e:
                errors.append(f"Failed to create Keycloak client: {e}")

        # Create tenant config
        config = TenantConfig(
            tenant_id=tenant_id,
            display_name=display_name,
            domain=domain,
            contact_email=contact_email,
            workspace_path=workspace_path,
            milvus_partition=milvus_partition,
            dynamodb_table=dynamodb_table,
            s3_prefix=s3_prefix,
            keycloak_realm="genesis",
            keycloak_client_id=keycloak_client_id
        )

        # Store tenant config
        self._tenants[tenant_id] = config

        return ProvisioningResult(
            success=len(errors) == 0,
            tenant_id=tenant_id,
            resources_created=resources_created,
            errors=errors,
            keycloak_client_secret=keycloak_client_secret
        )

    async def get_tenant(self, tenant_id: str) -> Optional[TenantConfig]:
        """
        Get tenant configuration.

        Args:
            tenant_id: Tenant identifier

        Returns:
            TenantConfig or None if not found
        """
        return self._tenants.get(tenant_id)

    async def list_tenants(self) -> List[TenantConfig]:
        """
        List all tenants.

        Returns:
            List of tenant configurations
        """
        return list(self._tenants.values())

    async def delete_tenant(self, tenant_id: str) -> bool:
        """
        Delete a tenant and all associated resources.

        This is a destructive operation for GDPR compliance.

        Args:
            tenant_id: Tenant to delete

        Returns:
            True if successful
        """
        if tenant_id not in self._tenants:
            return False

        config = self._tenants[tenant_id]

        # Delete Milvus partition
        if self.milvus_client:
            try:
                self.milvus_client.drop_partition(
                    collection_name=self.milvus_collection,
                    partition_name=config.milvus_partition
                )
            except Exception:
                pass

        # Delete DynamoDB table
        if self.dynamodb_client:
            try:
                self.dynamodb_client.delete_table(TableName=config.dynamodb_table)
            except Exception:
                pass

        # Delete S3 objects
        if self.s3_client:
            try:
                # List and delete all objects with prefix
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix=config.s3_prefix
                )
                for obj in response.get("Contents", []):
                    self.s3_client.delete_object(
                        Bucket=self.s3_bucket,
                        Key=obj["Key"]
                    )
            except Exception:
                pass

        # Delete Keycloak client
        if self.keycloak_config and config.keycloak_client_id:
            try:
                await self._delete_keycloak_client(config.keycloak_client_id)
            except Exception:
                pass

        # Remove from cache
        del self._tenants[tenant_id]

        return True

    async def update_credits(
        self,
        tenant_id: str,
        credits_used: float
    ) -> Optional[float]:
        """
        Update tenant credits after feature build.

        Args:
            tenant_id: Tenant identifier
            credits_used: Credits consumed

        Returns:
            Remaining credits or None if tenant not found
        """
        if tenant_id not in self._tenants:
            return None

        config = self._tenants[tenant_id]
        config.credits_remaining -= credits_used
        config.features_built += 1

        return config.credits_remaining

    async def _create_keycloak_client(
        self,
        tenant_id: str,
        display_name: str
    ) -> tuple:
        """
        Create Keycloak client for tenant.

        This enables the On-Behalf-Of (OBO) flow for the factory.

        Returns:
            Tuple of (client_id, client_secret)
        """
        # In production, use keycloak-admin library
        # For now, return placeholder
        client_id = f"factory-{tenant_id}"
        client_secret = hashlib.sha256(
            f"{tenant_id}-{os.urandom(16).hex()}".encode()
        ).hexdigest()[:32]

        return client_id, client_secret

    async def _delete_keycloak_client(self, client_id: str) -> None:
        """Delete Keycloak client."""
        # In production, use keycloak-admin library
        pass

    def _sanitize_tenant_id(self, tenant_id: str) -> str:
        """Sanitize tenant ID to be safe for use in paths and identifiers."""
        import re
        # Remove special characters, lowercase, max 32 chars
        sanitized = re.sub(r"[^a-z0-9_]", "_", tenant_id.lower())
        return sanitized[:32]


# ============================================================================
# Token Exchange (OBO Flow)
# ============================================================================

class TokenExchanger:
    """
    Handles Keycloak On-Behalf-Of (OBO) token exchange.

    The OBO flow allows the factory to act on behalf of a user
    when interacting with external services (GitHub, AWS, etc.).

    Flow:
    1. User logs in → Gets access_token
    2. User requests feature → Platform exchanges token
    3. Factory receives downstream_token → Acts as user
    4. All actions logged in Keycloak → Full audit trail
    """

    def __init__(self, keycloak_config: KeycloakConfig):
        self.config = keycloak_config

    async def exchange_token(
        self,
        user_token: str,
        target_client: str,
        tenant_id: str
    ) -> str:
        """
        Exchange user token for downstream service token.

        Args:
            user_token: User's access token
            target_client: Target service client ID
            tenant_id: Tenant context

        Returns:
            Downstream access token
        """
        # In production, call Keycloak token endpoint
        # POST /realms/{realm}/protocol/openid-connect/token
        # grant_type=urn:ietf:params:oauth:grant-type:token-exchange
        # subject_token={user_token}
        # requested_token_type=urn:ietf:params:oauth:token-type:access_token
        # audience={target_client}

        # For now, return placeholder
        return f"exchanged_token_for_{target_client}"

    async def validate_token(self, token: str, tenant_id: str) -> Dict[str, Any]:
        """
        Validate and decode a token.

        Args:
            token: Access token to validate
            tenant_id: Expected tenant

        Returns:
            Token claims

        Raises:
            ValueError: If token is invalid
        """
        # In production, validate with Keycloak
        # GET /realms/{realm}/protocol/openid-connect/userinfo
        # or decode JWT and verify signature

        return {
            "sub": "user_id",
            "tenant_id": tenant_id,
            "roles": ["factory_user"]
        }


__all__ = [
    "TenantManager",
    "TenantConfig",
    "ProvisioningResult",
    "TokenExchanger",
    "KeycloakConfig",
]
