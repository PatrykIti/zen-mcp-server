"""Custom API provider implementation."""

import logging
import os
from typing import Optional

from .openai_compatible import OpenAICompatibleProvider
from .openrouter_registry import OpenRouterModelRegistry
from .shared import ModelCapabilities, ModelResponse, ProviderType


class CustomProvider(OpenAICompatibleProvider):
    """Adapter for self-hosted or local OpenAI-compatible endpoints.

    Role
        Provide a uniform bridge between the MCP server and user-managed
        OpenAI-compatible services (Ollama, vLLM, LM Studio, bespoke gateways).
        By subclassing :class:`OpenAICompatibleProvider` it inherits request and
        token handling, while the custom registry exposes locally defined model
        metadata.

    Notable behaviour
        * Uses :class:`OpenRouterModelRegistry` to load model definitions and
          aliases so custom deployments share the same metadata pipeline as
          OpenRouter itself.
        * Normalises version-tagged model names (``model:latest``) and applies
          restriction policies just like cloud providers, ensuring consistent
          behaviour across environments.
    """

    FRIENDLY_NAME = "Custom API"

    # Model registry for managing configurations and aliases (shared with OpenRouter)
    _registry: Optional[OpenRouterModelRegistry] = None

    def __init__(self, api_key: str = "", base_url: str = "", **kwargs):
        """Initialize Custom provider for local/self-hosted models.

        This provider supports any OpenAI-compatible API endpoint including:
        - Ollama (typically no API key required)
        - vLLM (may require API key)
        - LM Studio (may require API key)
        - Text Generation WebUI (may require API key)
        - Enterprise/self-hosted APIs (typically require API key)

        Args:
            api_key: API key for the custom endpoint. Can be empty string for
                    providers that don't require authentication (like Ollama).
                    Falls back to CUSTOM_API_KEY environment variable if not provided.
            base_url: Base URL for the custom API endpoint (e.g., 'http://localhost:11434/v1').
                     Falls back to CUSTOM_API_URL environment variable if not provided.
            **kwargs: Additional configuration passed to parent OpenAI-compatible provider

        Raises:
            ValueError: If no base_url is provided via parameter or environment variable
        """
        # Fall back to environment variables only if not provided
        if not base_url:
            base_url = os.getenv("CUSTOM_API_URL", "")
        if not api_key:
            api_key = os.getenv("CUSTOM_API_KEY", "")

        if not base_url:
            raise ValueError(
                "Custom API URL must be provided via base_url parameter or CUSTOM_API_URL environment variable"
            )

        # For Ollama and other providers that don't require authentication,
        # set a dummy API key to avoid OpenAI client header issues
        if not api_key:
            api_key = "dummy-key-for-unauthenticated-endpoint"
            logging.debug("Using dummy API key for unauthenticated custom endpoint")

        logging.info(f"Initializing Custom provider with endpoint: {base_url}")

        super().__init__(api_key, base_url=base_url, **kwargs)

        # Initialize model registry (shared with OpenRouter for consistent aliases)
        if CustomProvider._registry is None:
            CustomProvider._registry = OpenRouterModelRegistry()
            # Log loaded models and aliases only on first load
            models = self._registry.list_models()
            aliases = self._registry.list_aliases()
            logging.info(f"Custom provider loaded {len(models)} models with {len(aliases)} aliases")

    # ------------------------------------------------------------------
    # Capability surface
    # ------------------------------------------------------------------
    def _lookup_capabilities(
        self,
        canonical_name: str,
        requested_name: Optional[str] = None,
    ) -> Optional[ModelCapabilities]:
        """Return capabilities for models explicitly marked as custom."""

        builtin = super()._lookup_capabilities(canonical_name, requested_name)
        if builtin is not None:
            return builtin

        registry_entry = self._registry.resolve(canonical_name)
        if registry_entry and getattr(registry_entry, "is_custom", False):
            registry_entry.provider = ProviderType.CUSTOM
            return registry_entry

        logging.debug(
            "Custom provider cannot resolve model '%s'; ensure it is declared with 'is_custom': true in custom_models.json",
            canonical_name,
        )
        return None

    def get_provider_type(self) -> ProviderType:
        """Identify this provider for restriction and logging logic."""

        return ProviderType.CUSTOM

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Request execution
    # ------------------------------------------------------------------

    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate content using the custom API.

        Args:
            prompt: User prompt to send to the model
            model_name: Name of the model to use
            system_prompt: Optional system prompt for model behavior
            temperature: Sampling temperature
            max_output_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            ModelResponse with generated content and metadata
        """
        # Resolve model alias to actual model name
        resolved_model = self._resolve_model_name(model_name)

        # Call parent method with resolved model name
        return super().generate_content(
            prompt=prompt,
            model_name=resolved_model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Registry helpers
    # ------------------------------------------------------------------

    def _resolve_model_name(self, model_name: str) -> str:
        """Resolve registry aliases and strip version tags for local models."""

        config = self._registry.resolve(model_name)
        if config:
            if config.model_name != model_name:
                logging.info(f"Resolved model alias '{model_name}' to '{config.model_name}'")
            return config.model_name

        if ":" in model_name:
            base_model = model_name.split(":")[0]
            logging.debug(f"Stripped version tag from '{model_name}' -> '{base_model}'")

            base_config = self._registry.resolve(base_model)
            if base_config:
                logging.info(f"Resolved base model '{base_model}' to '{base_config.model_name}'")
                return base_config.model_name
            return base_model

        logging.debug(f"Model '{model_name}' not found in registry, using as-is")
        return model_name

    def get_all_model_capabilities(self) -> dict[str, ModelCapabilities]:
        """Expose registry capabilities for models marked as custom."""

        if not self._registry:
            return {}

        capabilities: dict[str, ModelCapabilities] = {}
        for model_name in self._registry.list_models():
            config = self._registry.resolve(model_name)
            if config and getattr(config, "is_custom", False):
                capabilities[model_name] = config
        return capabilities
