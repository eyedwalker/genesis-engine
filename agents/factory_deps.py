"""
Shared dependencies and tools for Hive BizOS Factory agents.

This module defines the dependency injection pattern and common tools
that all agents can access.
"""

from dataclasses import dataclass
from typing import List, Optional, Any
import boto3
import os
from pymilvus import MilvusClient
import json
from pydantic_ai import RunContext


@dataclass
class FactoryDeps:
    """
    Dependency injection container for factory agents.
    
    All agents receive this object and can access:
    - Milvus client for RAG
    - DynamoDB for caching
    - S3 for file storage
    - Workspace path for code generation
    - Tenant ID for multi-tenancy
    """
    milvus_client: Optional[MilvusClient]
    dynamodb_client: Any  # boto3 DynamoDB client
    s3_client: Any  # boto3 S3 client
    tenant_id: str
    workspace_root: str
    
    @classmethod
    def from_env(cls) -> "FactoryDeps":
        """
        Create dependencies from environment variables.
        
        Required env vars:
        - MILVUS_URI: Connection string for Milvus
        - AWS_REGION: AWS region (default: us-east-1)
        - TENANT_ID: Unique tenant identifier
        - WORKSPACE_ROOT: Path for generated code
        
        Returns:
            Configured FactoryDeps instance
        """
        # Milvus connection (optional - can use self-hosted or Zilliz)
        milvus_uri = os.getenv("MILVUS_URI")
        milvus_client = None
        if milvus_uri:
            try:
                milvus_client = MilvusClient(uri=milvus_uri)
            except Exception as e:
                print(f"Warning: Could not connect to Milvus: {e}")
        
        # AWS clients (using free tier services)
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        dynamodb = boto3.client("dynamodb", region_name=aws_region)
        s3 = boto3.client("s3", region_name=aws_region)
        
        return cls(
            milvus_client=milvus_client,
            dynamodb_client=dynamodb,
            s3_client=s3,
            tenant_id=os.getenv("TENANT_ID", "default"),
            workspace_root=os.getenv("WORKSPACE_ROOT", "/tmp/workspace")
        )


# ============================================================================
# Tool Definitions
# ============================================================================

async def search_fhir_docs(ctx: RunContext[FactoryDeps], query: str) -> str:
    """
    Search the FHIR documentation stored in Milvus.
    
    Use this tool to find:
    - Valid field names for FHIR resources
    - Status code enumerations
    - Business rules and constraints
    - Example implementations
    
    Args:
        deps: Factory dependencies with Milvus client
        query: Natural language search query
        
    Returns:
        Relevant FHIR documentation as text
        
    Example:
        >>> docs = await search_fhir_docs(
        ...     deps,
        ...     "What are valid status values for Appointment?"
        ... )
        >>> print(docs)
        "Appointment.status must be one of: proposed, pending, booked..."
    """
    if not ctx.deps.milvus_client:
        return (
            "WARNING: Milvus not available. Using fallback FHIR knowledge.\n\n"
            "Appointment Resource:\n"
            "- status: proposed | pending | booked | arrived | fulfilled | "
            "cancelled | noshow | entered-in-error | checked-in | waitlist\n"
            "- participants: List of participants (required)\n"
            "- start: DateTime (required)\n"
            "- end: DateTime (required)\n"
            "- serviceType: CodeableConcept\n"
            "- account: Reference to Account resource"
        )
    
    try:
        # Search with partition isolation for multi-tenancy
        results = ctx.deps.milvus_client.search(
            collection_name="fhir_knowledge_base",
            data=[query],  # Embedding handled by Milvus
            filter=f"tenant_id == '{ctx.deps.tenant_id}'",
            limit=3,
            output_fields=["content", "source"]
        )
        
        # Format results
        docs = []
        for result in results[0]:  # First query's results
            entity = result['entity']
            content = entity.get('content', '')
            source = entity.get('source', 'Unknown')
            docs.append(f"Source: {source}\n{content}")
        
        return "\n\n---\n\n".join(docs) if docs else "No relevant documentation found."
        
    except Exception as e:
        return f"Error searching FHIR docs: {str(e)}\n\nUsing fallback knowledge."


async def read_code_file(ctx: RunContext[FactoryDeps], filepath: str) -> str:
    """
    Read an existing code file from the workspace.
    
    Use this to:
    - Review existing implementations
    - Check for duplicate functionality
    - Understand current architecture
    
    Args:
        deps: Factory dependencies
        filepath: Relative path from workspace root
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path traversal attempted
    """
    # Security check: Prevent path traversal
    if ".." in filepath or filepath.startswith("/"):
        raise ValueError(f"Invalid filepath: {filepath}. Must be relative.")
    
    full_path = os.path.join(ctx.deps.workspace_root, filepath)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(full_path, "r") as f:
        return f.read()


async def write_code_file(ctx: RunContext[FactoryDeps], filepath: str, content: str) -> str:
    """
    Write code to the workspace.
    
    Use this to:
    - Create new Python modules
    - Generate models, services, APIs
    - Create test files
    
    Args:
        deps: Factory dependencies
        filepath: Relative path from workspace root
        content: File content to write
        
    Returns:
        Success message with file size
        
    Raises:
        ValueError: If path traversal attempted
        
    Example:
        >>> result = await write_code_file(
        ...     deps,
        ...     "app/models/appointment.py",
        ...     "class Appointment(SQLModel): ..."
        ... )
        >>> print(result)
        "Successfully wrote 1234 bytes to app/models/appointment.py"
    """
    # Security check: Prevent path traversal
    if ".." in filepath or filepath.startswith("/"):
        raise ValueError(f"Invalid filepath: {filepath}. Must be relative.")
    
    full_path = os.path.join(ctx.deps.workspace_root, filepath)
    
    # Create parent directories if needed
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Write file
    with open(full_path, "w") as f:
        f.write(content)
    
    # Return success message
    size = len(content.encode('utf-8'))
    return f"Successfully wrote {size} bytes to {filepath}"


async def cache_get(ctx: RunContext[FactoryDeps], key: str) -> Optional[str]:
    """
    Get value from DynamoDB cache.
    
    Use this to:
    - Retrieve cached API responses
    - Get previously generated code
    - Check if feature already exists
    
    Args:
        deps: Factory dependencies with DynamoDB client
        key: Cache key
        
    Returns:
        Cached value or None if not found
    """
    try:
        table_name = f"factory-cache-{ctx.deps.tenant_id}"
        
        response = ctx.deps.dynamodb_client.get_item(
            TableName=table_name,
            Key={"key": {"S": key}}
        )
        
        if "Item" in response:
            return response["Item"]["value"]["S"]
        return None
        
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


async def cache_set(
    ctx: RunContext[FactoryDeps],
    key: str,
    value: str,
    ttl_seconds: int = 3600
) -> bool:
    """
    Set value in DynamoDB cache with TTL.
    
    Args:
        deps: Factory dependencies
        key: Cache key
        value: Value to cache
        ttl_seconds: Time to live in seconds (default: 1 hour)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import time
        
        table_name = f"factory-cache-{ctx.deps.tenant_id}"
        ttl = int(time.time()) + ttl_seconds
        
        ctx.deps.dynamodb_client.put_item(
            TableName=table_name,
            Item={
                "key": {"S": key},
                "value": {"S": value},
                "ttl": {"N": str(ttl)}
            }
        )
        return True
        
    except Exception as e:
        print(f"Cache set error: {e}")
        return False


async def list_workspace_files(ctx: RunContext[FactoryDeps], directory: str = "") -> List[str]:
    """
    List files in the workspace directory.
    
    Use this to:
    - See what files exist
    - Check for conflicts
    - Review structure
    
    Args:
        deps: Factory dependencies
        directory: Subdirectory to list (relative to workspace root)
        
    Returns:
        List of relative filepaths
    """
    if ".." in directory:
        raise ValueError(f"Invalid directory: {directory}")
    
    full_path = os.path.join(ctx.deps.workspace_root, directory)
    
    if not os.path.exists(full_path):
        return []
    
    files = []
    for root, _, filenames in os.walk(full_path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            # Make relative to workspace root
            rel_path = os.path.relpath(filepath, ctx.deps.workspace_root)
            files.append(rel_path)
    
    return sorted(files)


# ============================================================================
# Export all tools for easy importing
# ============================================================================

__all__ = [
    "FactoryDeps",
    "search_fhir_docs",
    "read_code_file",
    "write_code_file",
    "cache_get",
    "cache_set",
    "list_workspace_files",
]
