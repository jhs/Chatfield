"""OpenRouter connector for DeepEval - enables use of 300+ models via OpenRouter API."""

import os
import json
from typing import Optional, Dict, Any
from openai import OpenAI
from deepeval.models.base_model import DeepEvalBaseLLM


class OpenRouterModel(DeepEvalBaseLLM):
    """
    Custom DeepEval LLM connector for OpenRouter.

    OpenRouter provides access to 300+ models through a unified OpenAI-compatible API.
    This connector allows DeepEval metrics to use any model available on OpenRouter.

    Example usage:
        model = OpenRouterModel(
            model="google/gemini-2.0-flash-thinking-exp",
            api_key=os.environ.get("OPENROUTER_API_KEY")
        )
        metric = ConversationalGEval(model=model, ...)
    """

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        base_url: str = "https://openrouter.ai/api/v1",
        site_url: Optional[str] = None,
        app_name: str = "Chatfield",
        timeout: float = 60.0,
        **kwargs
    ):
        """
        Initialize OpenRouter model connector.

        Args:
            model: OpenRouter model identifier (e.g., "google/gemini-2.0-flash")
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            temperature: Generation temperature (0.0-1.0)
            base_url: OpenRouter API endpoint
            site_url: Optional site URL for attribution
            app_name: Application name for OpenRouter headers
            timeout: Request timeout in seconds (default: 60.0)
            **kwargs: Additional OpenAI client parameters
        """
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not provided. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key parameter."
            )

        # Initialize OpenAI client with OpenRouter configuration
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
            timeout=timeout,
            default_headers={
                "HTTP-Referer": site_url or os.environ.get("SITE_URL", ""),
                "X-Title": app_name
            },
            **kwargs
        )

        # Cache for model object
        self._model = None

    def load_model(self):
        """Return the model client object."""
        if self._model is None:
            self._model = self.client
        return self._model

    def generate(self, prompt: str) -> str:
        """
        Generate a response for the given prompt.

        Args:
            prompt: The input prompt string

        Returns:
            The generated response string
        """
        client = self.load_model()

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=4096,
                timeout=self.timeout,
            )
            return response.choices[0].message.content
        except Exception as e:
            # Handle OpenRouter-specific errors
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                raise RuntimeError(
                    f"OpenRouter request timed out after {self.timeout}s for model {self.model}. "
                    f"Consider increasing timeout or using a faster model."
                )
            elif "rate limit" in error_msg.lower():
                raise RuntimeError(f"OpenRouter rate limit exceeded for model {self.model}: {error_msg}")
            elif "invalid model" in error_msg.lower():
                raise ValueError(f"Invalid OpenRouter model: {self.model}")
            else:
                raise RuntimeError(f"OpenRouter API error: {error_msg}")

    async def a_generate(self, prompt: str) -> str:
        """
        Async version of generate method.

        Args:
            prompt: The input prompt string

        Returns:
            The generated response string
        """
        # For simplicity, using sync client in async context
        # Could be improved with httpx or aiohttp for true async
        return self.generate(prompt)

    def get_model_name(self) -> str:
        """
        Return the model name for identification.

        Returns:
            The OpenRouter model identifier
        """
        return f"openrouter:{self.model}"

    def generate_with_schema(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured output conforming to a JSON schema.

        Args:
            prompt: The input prompt string
            schema: JSON schema for the expected output

        Returns:
            Parsed JSON response conforming to the schema
        """
        client = self.load_model()

        # Add schema instruction to prompt
        schema_prompt = (
            f"{prompt}\n\n"
            f"Please respond with valid JSON that conforms to this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```"
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": schema_prompt}],
                temperature=self.temperature,
                max_tokens=4096,
                timeout=self.timeout,
                response_format={"type": "json_object"} if self._supports_json_mode() else None
            )

            content = response.choices[0].message.content

            # Parse and validate JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                raise ValueError(f"Failed to parse JSON from OpenRouter response: {e}")

        except Exception as e:
            error_msg = str(e)
            if "rate limit" in error_msg.lower():
                raise RuntimeError(f"OpenRouter rate limit exceeded for model {self.model}: {error_msg}")
            else:
                raise RuntimeError(f"OpenRouter API error: {error_msg}")

    def _supports_json_mode(self) -> bool:
        """
        Check if the model supports JSON response format.

        Returns:
            True if model supports JSON mode, False otherwise
        """
        # Models known to support JSON mode
        json_mode_models = [
            "openai/gpt",
            "anthropic/claude",
            "google/gemini-2",
            "mistral/mistral-large"
        ]

        return any(self.model.startswith(prefix) for prefix in json_mode_models)