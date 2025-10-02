"""Base interfaces and common behaviour for model providers."""

import base64
import binascii
import logging
import os
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from tools.models import ToolModelCategory

from utils.file_types import IMAGES, get_image_mime_type

from .shared import ModelCapabilities, ModelResponse, ProviderType

logger = logging.getLogger(__name__)


class ModelProvider(ABC):
    """Abstract base class for all model backends in the MCP server.

    Role
        Defines the interface every provider must implement so the registry,
        restriction service, and tools have a uniform surface for listing
        models, resolving aliases, and executing requests.

    Responsibilities
        * expose static capability metadata for each supported model via
          :class:`ModelCapabilities`
        * accept user prompts, forward them to the underlying SDK, and wrap
          responses in :class:`ModelResponse`
        * report tokenizer counts for budgeting and validation logic
        * advertise provider identity (``ProviderType``) so restriction
          policies can map environment configuration onto providers
        * validate whether a model name or alias is recognised by the provider

    Shared helpers like temperature validation, alias resolution, and
    restriction-aware ``list_models`` live here so concrete subclasses only
    need to supply their catalogue and wire up SDK-specific behaviour.
    """

    # All concrete providers must define their supported models
    MODEL_CAPABILITIES: dict[str, Any] = {}

    # Default maximum image size in MB
    DEFAULT_MAX_IMAGE_SIZE_MB = 20.0

    def __init__(self, api_key: str, **kwargs):
        """Initialize the provider with API key and optional configuration."""
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a specific model."""
        pass

    @abstractmethod
    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate content using the model.

        Args:
            prompt: User prompt to send to the model
            model_name: Name of the model to use
            system_prompt: Optional system prompt for model behavior
            temperature: Sampling temperature (0-2)
            max_output_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters

        Returns:
            ModelResponse with generated content and metadata
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str, model_name: str) -> int:
        """Count tokens for the given text using the specified model's tokenizer."""
        pass

    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        pass

    @abstractmethod
    def validate_model_name(self, model_name: str) -> bool:
        """Validate if the model name is supported by this provider."""
        pass

    def validate_parameters(self, model_name: str, temperature: float, **kwargs) -> None:
        """Validate model parameters against capabilities.

        Raises:
            ValueError: If parameters are invalid
        """
        capabilities = self.get_capabilities(model_name)

        # Validate temperature using constraint
        if not capabilities.temperature_constraint.validate(temperature):
            constraint_desc = capabilities.temperature_constraint.get_description()
            raise ValueError(f"Temperature {temperature} is invalid for model {model_name}. {constraint_desc}")

    @abstractmethod
    def supports_thinking_mode(self, model_name: str) -> bool:
        """Check if the model supports extended thinking mode."""
        pass

    def get_model_configurations(self) -> dict[str, ModelCapabilities]:
        """Get model configurations for this provider.

        This is a hook method that subclasses can override to provide
        their model configurations from different sources.

        Returns:
            Dictionary mapping model names to their ModelCapabilities objects
        """
        model_map = getattr(self, "MODEL_CAPABILITIES", None)
        if isinstance(model_map, dict) and model_map:
            return {k: v for k, v in model_map.items() if isinstance(v, ModelCapabilities)}
        return {}

    def _resolve_model_name(self, model_name: str) -> str:
        """Resolve model shorthand to full name.

        This implementation uses the hook methods to support different
        model configuration sources.

        Args:
            model_name: Model name that may be an alias

        Returns:
            Resolved model name
        """
        # Get model configurations from the hook method
        model_configs = self.get_model_configurations()

        # First check if it's already a base model name (case-sensitive exact match)
        if model_name in model_configs:
            return model_name

        # Check case-insensitively for both base models and aliases
        model_name_lower = model_name.lower()

        # Check base model names case-insensitively
        for base_model in model_configs:
            if base_model.lower() == model_name_lower:
                return base_model

        # Check aliases from the model configurations
        alias_map = ModelCapabilities.collect_aliases(model_configs)
        for base_model, aliases in alias_map.items():
            if any(alias.lower() == model_name_lower for alias in aliases):
                return base_model

        # If not found, return as-is
        return model_name

    def list_models(
        self,
        *,
        respect_restrictions: bool = True,
        include_aliases: bool = True,
        lowercase: bool = False,
        unique: bool = False,
    ) -> list[str]:
        """Return formatted model names supported by this provider.

        Args:
            respect_restrictions: Apply provider restriction policy.
            include_aliases: Include aliases alongside canonical model names.
            lowercase: Normalize returned names to lowercase.
            unique: Deduplicate names after formatting.

        Returns:
            List of model names formatted according to the provided options.
        """

        model_configs = self.get_model_configurations()
        if not model_configs:
            return []

        restriction_service = None
        if respect_restrictions:
            from utils.model_restrictions import get_restriction_service

            restriction_service = get_restriction_service()

        if restriction_service:
            allowed_configs = {}
            for model_name, config in model_configs.items():
                if restriction_service.is_allowed(self.get_provider_type(), model_name):
                    allowed_configs[model_name] = config
            model_configs = allowed_configs

        if not model_configs:
            return []

        return ModelCapabilities.collect_model_names(
            model_configs,
            include_aliases=include_aliases,
            lowercase=lowercase,
            unique=unique,
        )

    def validate_image(self, image_path: str, max_size_mb: float = None) -> tuple[bytes, str]:
        """Provider-independent image validation.

        Args:
            image_path: Path to image file or data URL
            max_size_mb: Maximum allowed image size in MB (defaults to DEFAULT_MAX_IMAGE_SIZE_MB)

        Returns:
            Tuple of (image_bytes, mime_type)

        Raises:
            ValueError: If image is invalid

        Examples:
            # Validate a file path
            image_bytes, mime_type = provider.validate_image("/path/to/image.png")

            # Validate a data URL
            image_bytes, mime_type = provider.validate_image("data:image/png;base64,...")

            # Validate with custom size limit
            image_bytes, mime_type = provider.validate_image("/path/to/image.jpg", max_size_mb=10.0)
        """
        # Use default if not specified
        if max_size_mb is None:
            max_size_mb = self.DEFAULT_MAX_IMAGE_SIZE_MB

        if image_path.startswith("data:"):
            # Parse data URL: data:image/png;base64,iVBORw0...
            try:
                header, data = image_path.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid data URL format: {e}")

            # Validate MIME type using IMAGES constant
            valid_mime_types = [get_image_mime_type(ext) for ext in IMAGES]
            if mime_type not in valid_mime_types:
                raise ValueError(f"Unsupported image type: {mime_type}. Supported types: {', '.join(valid_mime_types)}")

            # Decode base64 data
            try:
                image_bytes = base64.b64decode(data)
            except binascii.Error as e:
                raise ValueError(f"Invalid base64 data: {e}")
        else:
            # Handle file path
            # Read file first to check if it exists
            try:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
            except FileNotFoundError:
                raise ValueError(f"Image file not found: {image_path}")
            except Exception as e:
                raise ValueError(f"Failed to read image file: {e}")

            # Validate extension
            ext = os.path.splitext(image_path)[1].lower()
            if ext not in IMAGES:
                raise ValueError(f"Unsupported image format: {ext}. Supported formats: {', '.join(sorted(IMAGES))}")

            # Get MIME type
            mime_type = get_image_mime_type(ext)

        # Validate size
        size_mb = len(image_bytes) / (1024 * 1024)
        if size_mb > max_size_mb:
            raise ValueError(f"Image too large: {size_mb:.1f}MB (max: {max_size_mb}MB)")

        return image_bytes, mime_type

    def close(self):
        """Clean up any resources held by the provider.

        Default implementation does nothing.
        Subclasses should override if they hold resources that need cleanup.
        """
        # Base implementation: no resources to clean up
        return

    def get_preferred_model(self, category: "ToolModelCategory", allowed_models: list[str]) -> Optional[str]:
        """Get the preferred model from this provider for a given category.

        Args:
            category: The tool category requiring a model
            allowed_models: Pre-filtered list of model names that are allowed by restrictions

        Returns:
            Model name if this provider has a preference, None otherwise
        """
        # Default implementation - providers can override with specific logic
        return None

    def get_model_registry(self) -> Optional[dict[str, Any]]:
        """Get the model registry for providers that maintain one.

        This is a hook method for providers like CustomProvider that maintain
        a dynamic model registry.

        Returns:
            Model registry dict or None if not applicable
        """
        # Default implementation - most providers don't have a registry
        return None
