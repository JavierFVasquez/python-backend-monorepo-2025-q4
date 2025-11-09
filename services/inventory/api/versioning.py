"""API versioning utilities and configuration."""
from enum import Enum


class APIVersion(str, Enum):
    """Supported API versions."""

    V1 = "v1"
    # V2 = "v2"  # Future versions

    @property
    def prefix(self) -> str:
        """Return the URL prefix for this version."""
        return f"/api/{self.value}"

    @property
    def is_deprecated(self) -> bool:
        """Check if this version is deprecated."""
        # V1 is current stable version
        return False

    def deprecation_info(self) -> dict[str, str] | None:
        """Return deprecation information if applicable."""
        if not self.is_deprecated:
            return None

        return {
            "sunset_date": "2026-06-01",
            "migration_guide": "https://docs.example.com/migration/v1-to-v2",
        }


# Current stable version
CURRENT_VERSION = APIVersion.V1

# Supported versions for routing
SUPPORTED_VERSIONS = [APIVersion.V1]

