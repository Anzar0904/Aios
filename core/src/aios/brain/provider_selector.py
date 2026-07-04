from typing import Optional

from aios.brain.models import BrainContext, ProviderSelection
from aios.services.model import ModelService


class ProviderSelector:
    def __init__(self, model_service: ModelService) -> None:
        self.model_service = model_service

    def select_provider(
        self, objective: str, context: Optional[BrainContext] = None
    ) -> ProviderSelection:
        obj_lower = objective.lower()
        
        # Rule-based heuristics to select model/provider
        if "mock" in obj_lower:
            model_name = "mock-model"
        elif "gpt" in obj_lower or "openai" in obj_lower:
            model_name = "gpt-4o"
        elif (
            "claude" in obj_lower
            or "sonnet" in obj_lower
            or "github" in obj_lower
            or "review" in obj_lower
            or "analyze" in obj_lower
        ):
            model_name = "claude-3-5-sonnet"
        elif "gemini" in obj_lower:
            model_name = "gemini-1.5-pro"
        elif "llama" in obj_lower or "ollama" in obj_lower:
            model_name = "llama3"
        else:
            # Default to model service's default model, or claude-3-5-sonnet
            model_name = getattr(self.model_service, "_default_model", None) or "claude-3-5-sonnet"

        try:
            provider_name = self.model_service.registry.get_provider_for_model(model_name)
        except Exception:
            # Graceful fallbacks
            if "mock" in model_name:
                provider_name = "mock"
            elif "claude" in model_name:
                provider_name = "claude"
            elif "gpt" in model_name:
                provider_name = "openai"
            elif "gemini" in model_name:
                provider_name = "gemini"
            else:
                provider_name = "mock"
                model_name = "mock-model"

        return ProviderSelection(
            provider_name=provider_name,
            model_name=model_name,
            reason=f"Selected {model_name} (provider: {provider_name}) based on objective keywords."
        )
