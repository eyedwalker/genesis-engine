"""
Reusable Environment Variable Templates.

Creates standardized .env templates based on domain and integrations.
Extracted from actual Genesis Engine .env patterns.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from genesis.standards import EnvironmentVariableSpec, EnvironmentVariableType


# ============================================================================
# Base Environment Templates
# ============================================================================

class BaseEnvTemplate(BaseModel):
    """Base environment template for all factories."""

    @staticmethod
    def get_ai_api_keys() -> List[EnvironmentVariableSpec]:
        """Standard AI API keys (from existing .env)."""
        return [
            EnvironmentVariableSpec(
                name="ANTHROPIC_API_KEY",
                description="Anthropic Claude API Key - Primary AI model",
                var_type=EnvironmentVariableType.API_KEY,
                required=True,
                example="sk-ant-api03-...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="OPENAI_API_KEY",
                description="OpenAI API Key - Fallback AI model",
                var_type=EnvironmentVariableType.API_KEY,
                required=False,
                example="sk-proj-...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="OPENAI_ORG_ID",
                description="OpenAI Organization ID",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                example="org-...",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="GROQ_API_KEY",
                description="Groq API Key - Fast inference for simple tasks",
                var_type=EnvironmentVariableType.API_KEY,
                required=False,
                example="gsk_...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="GOOGLE_API_KEY",
                description="Google Gemini API Key - Alternative AI model",
                var_type=EnvironmentVariableType.API_KEY,
                required=False,
                example="AIza...",
                sensitive=True
            ),
        ]

    @staticmethod
    def get_database_config() -> List[EnvironmentVariableSpec]:
        """Standard database configuration."""
        return [
            EnvironmentVariableSpec(
                name="DATABASE_URL",
                description="PostgreSQL connection string",
                var_type=EnvironmentVariableType.DATABASE_URL,
                required=True,
                example="postgresql://user:pass@localhost:5432/dbname",
                sensitive=True,
                validation="^postgresql://.*"
            ),
            EnvironmentVariableSpec(
                name="DB_POOL_SIZE",
                description="Database connection pool size",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="10",
                example="20",
                validation="^[0-9]+$",
                sensitive=False
            ),
        ]

    @staticmethod
    def get_genesis_config() -> List[EnvironmentVariableSpec]:
        """Genesis Engine specific configuration (from existing .env)."""
        return [
            EnvironmentVariableSpec(
                name="USE_DAGGER",
                description="Use Dagger for containerized builds (requires Docker)",
                var_type=EnvironmentVariableType.FEATURE_FLAG,
                required=False,
                default_value="true",
                example="false",
                validation="true|false",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="MAX_ITERATIONS",
                description="Maximum self-healing iterations before escalation",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="5",
                example="10",
                validation="^[0-9]+$",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="GENESIS_WORKSPACE",
                description="Genesis workspace for factory blueprints",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="/tmp/genesis",
                example="./workspace/genesis",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="WORKSPACE_ROOT",
                description="Root directory for generated code",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="./workspace",
                example="./generated",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="TENANT_ID",
                description="Tenant ID for multi-tenancy",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="default",
                example="company_abc",
                sensitive=False
            ),
        ]

    @staticmethod
    def get_milvus_config() -> List[EnvironmentVariableSpec]:
        """Milvus vector database configuration (from existing .env)."""
        return [
            EnvironmentVariableSpec(
                name="MILVUS_URI",
                description="Milvus connection string for vector search",
                var_type=EnvironmentVariableType.SERVICE_URL,
                required=False,
                default_value="http://localhost:19530",
                example="http://milvus:19530",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="MILVUS_COLLECTION",
                description="Milvus collection name for knowledge base",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="factory_knowledge",
                example="healthcare_knowledge",
                sensitive=False
            ),
        ]

    @staticmethod
    def get_keycloak_config() -> List[EnvironmentVariableSpec]:
        """Keycloak identity management configuration (from existing .env)."""
        return [
            EnvironmentVariableSpec(
                name="KEYCLOAK_URL",
                description="Keycloak server URL",
                var_type=EnvironmentVariableType.SERVICE_URL,
                required=False,
                default_value="http://localhost:8080",
                example="https://auth.company.com",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="KEYCLOAK_REALM",
                description="Keycloak realm name",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="genesis",
                example="production",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="KEYCLOAK_CLIENT_ID",
                description="Keycloak client ID",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="genesis-engine",
                example="my-app",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="KEYCLOAK_CLIENT_SECRET",
                description="Keycloak client secret",
                var_type=EnvironmentVariableType.SECRET,
                required=False,
                example="abc123...",
                sensitive=True
            ),
        ]

    @staticmethod
    def get_aws_config() -> List[EnvironmentVariableSpec]:
        """AWS configuration (from existing .env)."""
        return [
            EnvironmentVariableSpec(
                name="AWS_REGION",
                description="AWS Region",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="us-east-1",
                example="us-west-2",
                validation="^[a-z]{2}-[a-z]+-[0-9]+$",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="AWS_ACCESS_KEY_ID",
                description="AWS Access Key ID (if not using AWS CLI)",
                var_type=EnvironmentVariableType.SECRET,
                required=False,
                example="AKIA...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="AWS_SECRET_ACCESS_KEY",
                description="AWS Secret Access Key",
                var_type=EnvironmentVariableType.SECRET,
                required=False,
                example="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="DYNAMODB_TABLE",
                description="DynamoDB table for factory state",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="genesis_factories",
                example="my_factories",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="S3_BUCKET",
                description="S3 bucket for artifacts",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="genesis-artifacts",
                example="my-artifacts",
                sensitive=False
            ),
        ]

    @staticmethod
    def get_optimization_flags() -> List[EnvironmentVariableSpec]:
        """Cost optimization flags (from existing .env)."""
        return [
            EnvironmentVariableSpec(
                name="OPTIMIZE_AI_COSTS",
                description="Use cheaper models for simple tasks",
                var_type=EnvironmentVariableType.FEATURE_FLAG,
                required=False,
                default_value="true",
                example="false",
                validation="true|false",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="ENABLE_PROMPT_CACHE",
                description="Enable Anthropic prompt caching to reduce costs",
                var_type=EnvironmentVariableType.FEATURE_FLAG,
                required=False,
                default_value="true",
                example="false",
                validation="true|false",
                sensitive=False
            ),
        ]

    @staticmethod
    def get_development_flags() -> List[EnvironmentVariableSpec]:
        """Development and testing flags (from existing .env)."""
        return [
            EnvironmentVariableSpec(
                name="LOG_LEVEL",
                description="Application log level",
                var_type=EnvironmentVariableType.CONFIG,
                required=False,
                default_value="INFO",
                example="DEBUG",
                validation="DEBUG|INFO|WARNING|ERROR",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="MOCK_AI",
                description="Skip actual AI calls and use mock responses",
                var_type=EnvironmentVariableType.FEATURE_FLAG,
                required=False,
                default_value="false",
                example="true",
                validation="true|false",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="DEBUG",
                description="Verbose debug output",
                var_type=EnvironmentVariableType.FEATURE_FLAG,
                required=False,
                default_value="false",
                example="true",
                validation="true|false",
                sensitive=False
            ),
        ]


# ============================================================================
# Domain-Specific Templates
# ============================================================================

class HealthcareEnvTemplate(BaseEnvTemplate):
    """Healthcare-specific environment variables."""

    @staticmethod
    def get_healthcare_vars() -> List[EnvironmentVariableSpec]:
        """FHIR and healthcare integrations."""
        return [
            EnvironmentVariableSpec(
                name="FHIR_SERVER_URL",
                description="FHIR R4 server endpoint",
                var_type=EnvironmentVariableType.SERVICE_URL,
                required=True,
                example="https://fhir.server.com/fhir/R4",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="FHIR_CLIENT_ID",
                description="FHIR server OAuth client ID",
                var_type=EnvironmentVariableType.CONFIG,
                required=True,
                example="my-app-client-id",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="FHIR_CLIENT_SECRET",
                description="FHIR server OAuth client secret",
                var_type=EnvironmentVariableType.SECRET,
                required=True,
                example="secret123",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="HIPAA_AUDIT_LOG_BUCKET",
                description="S3 bucket for HIPAA audit logs",
                var_type=EnvironmentVariableType.CONFIG,
                required=True,
                example="hipaa-audit-logs",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="PHI_ENCRYPTION_KEY_ID",
                description="KMS key ID for PHI encryption",
                var_type=EnvironmentVariableType.SECRET,
                required=True,
                example="arn:aws:kms:...",
                sensitive=True
            ),
        ]


class EcommerceEnvTemplate(BaseEnvTemplate):
    """E-commerce specific environment variables."""

    @staticmethod
    def get_ecommerce_vars() -> List[EnvironmentVariableSpec]:
        """Payment and commerce integrations."""
        return [
            EnvironmentVariableSpec(
                name="STRIPE_API_KEY",
                description="Stripe API key for payment processing",
                var_type=EnvironmentVariableType.API_KEY,
                required=True,
                example="sk_test_51...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="STRIPE_WEBHOOK_SECRET",
                description="Stripe webhook signing secret",
                var_type=EnvironmentVariableType.SECRET,
                required=True,
                example="whsec_...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="SHIPSTATION_API_KEY",
                description="ShipStation API key for shipping",
                var_type=EnvironmentVariableType.API_KEY,
                required=False,
                example="abc123...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="SENDGRID_API_KEY",
                description="SendGrid for transactional emails",
                var_type=EnvironmentVariableType.API_KEY,
                required=True,
                example="SG.abc123...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="PRODUCT_IMAGE_CDN",
                description="CDN URL for product images",
                var_type=EnvironmentVariableType.SERVICE_URL,
                required=False,
                default_value="https://cdn.cloudflare.com",
                example="https://images.mystore.com",
                sensitive=False
            ),
        ]


class FintechEnvTemplate(BaseEnvTemplate):
    """Fintech specific environment variables."""

    @staticmethod
    def get_fintech_vars() -> List[EnvironmentVariableSpec]:
        """Financial services integrations."""
        return [
            EnvironmentVariableSpec(
                name="PLAID_CLIENT_ID",
                description="Plaid API client ID for bank connections",
                var_type=EnvironmentVariableType.CONFIG,
                required=True,
                example="abc123...",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="PLAID_SECRET",
                description="Plaid API secret",
                var_type=EnvironmentVariableType.SECRET,
                required=True,
                example="secret123...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="PLAID_ENVIRONMENT",
                description="Plaid environment (sandbox, development, production)",
                var_type=EnvironmentVariableType.CONFIG,
                required=True,
                default_value="sandbox",
                example="production",
                validation="sandbox|development|production",
                sensitive=False
            ),
            EnvironmentVariableSpec(
                name="FRAUD_DETECTION_API_KEY",
                description="Fraud detection service API key",
                var_type=EnvironmentVariableType.API_KEY,
                required=False,
                example="fd_abc123...",
                sensitive=True
            ),
            EnvironmentVariableSpec(
                name="KYC_PROVIDER_API_KEY",
                description="KYC/AML provider API key",
                var_type=EnvironmentVariableType.API_KEY,
                required=True,
                example="kyc_abc123...",
                sensitive=True
            ),
        ]


# ============================================================================
# Template Builder
# ============================================================================

class EnvTemplateBuilder:
    """Build complete environment templates for different domains."""

    @staticmethod
    def build_base_template() -> List[EnvironmentVariableSpec]:
        """Base template for all factories."""
        return (
            BaseEnvTemplate.get_ai_api_keys() +
            BaseEnvTemplate.get_genesis_config() +
            BaseEnvTemplate.get_database_config() +
            BaseEnvTemplate.get_milvus_config() +
            BaseEnvTemplate.get_keycloak_config() +
            BaseEnvTemplate.get_optimization_flags() +
            BaseEnvTemplate.get_development_flags()
        )

    @staticmethod
    def build_healthcare_template() -> List[EnvironmentVariableSpec]:
        """Complete healthcare factory template."""
        return (
            EnvTemplateBuilder.build_base_template() +
            HealthcareEnvTemplate.get_healthcare_vars()
        )

    @staticmethod
    def build_ecommerce_template() -> List[EnvironmentVariableSpec]:
        """Complete e-commerce factory template."""
        return (
            EnvTemplateBuilder.build_base_template() +
            EcommerceEnvTemplate.get_ecommerce_vars()
        )

    @staticmethod
    def build_fintech_template() -> List[EnvironmentVariableSpec]:
        """Complete fintech factory template."""
        return (
            EnvTemplateBuilder.build_base_template() +
            FintechEnvTemplate.get_fintech_vars()
        )

    @staticmethod
    def build_with_aws(base_vars: List[EnvironmentVariableSpec]) -> List[EnvironmentVariableSpec]:
        """Add AWS configuration to any template."""
        return base_vars + BaseEnvTemplate.get_aws_config()

    @staticmethod
    def generate_env_file(
        vars: List[EnvironmentVariableSpec],
        project_name: str,
        include_notes: bool = True
    ) -> str:
        """Generate .env.example file content."""
        lines = [
            f"# {project_name} - Environment Variables",
            "# Copy this file to .env and fill in your values",
            ""
        ]

        # Group by type
        groups = {
            "AI API Keys": [],
            "Database": [],
            "Services": [],
            "Configuration": [],
            "Feature Flags": [],
            "Secrets": [],
        }

        for var in vars:
            if var.var_type == EnvironmentVariableType.API_KEY:
                groups["AI API Keys"].append(var)
            elif var.var_type == EnvironmentVariableType.DATABASE_URL:
                groups["Database"].append(var)
            elif var.var_type == EnvironmentVariableType.SERVICE_URL:
                groups["Services"].append(var)
            elif var.var_type == EnvironmentVariableType.FEATURE_FLAG:
                groups["Feature Flags"].append(var)
            elif var.var_type == EnvironmentVariableType.SECRET:
                groups["Secrets"].append(var)
            else:
                groups["Configuration"].append(var)

        for group_name, group_vars in groups.items():
            if not group_vars:
                continue

            lines.append(f"# {'='*76}")
            lines.append(f"# {group_name}")
            lines.append(f"# {'='*76}")
            lines.append("")

            for var in group_vars:
                # Description
                lines.append(f"# {var.description}")

                # Required/Optional
                if not var.required:
                    lines.append("# (Optional)")

                # Example
                if var.example:
                    lines.append(f"# Example: {var.example}")

                # Validation
                if var.validation:
                    lines.append(f"# Valid values: {var.validation}")

                # Variable
                if var.required:
                    lines.append(f"{var.name}=")
                else:
                    default = var.default_value or ""
                    lines.append(f"{var.name}={default}")

                lines.append("")

        if include_notes:
            lines.extend([
                f"# {'='*76}",
                "# Notes",
                f"# {'='*76}",
                "",
                "# 1. NEVER commit .env to Git!",
                "#    Add .env to .gitignore",
                "#",
                "# 2. Required variables must be filled in",
                "#",
                "# 3. All other variables have defaults",
                "",
            ])

        return "\n".join(lines)


# ============================================================================
# Export
# ============================================================================

__all__ = [
    "BaseEnvTemplate",
    "HealthcareEnvTemplate",
    "EcommerceEnvTemplate",
    "FintechEnvTemplate",
    "EnvTemplateBuilder",
]
