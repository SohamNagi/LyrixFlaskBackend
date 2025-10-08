import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI


class GPTService:
    def __init__(self):
        self.model = "gpt-5-nano-2025-08-07"  # Updated model name
        self.api_key = os.getenv("LYRIXOPENAIKEY")

        if not self.api_key:
            raise ValueError("LYRIXOPENAIKEY environment variable is required")

        self.client = OpenAI(api_key=self.api_key)

    def generate_theme(self, lyrics: str, language: str) -> str:
        """Generate a theme summary for the song"""
        prompt = self._create_theme_prompt(language)

        try:
            response = self._make_theme_request(prompt, lyrics)
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to generate theme: {e}") from e

    def generate_analysis(self, lyrics: str, line: str, language_code: Optional[str] = None) -> Dict[str, str]:
        """Generate structured analysis for a specific line"""
        prompt = self._create_analysis_prompt()

        try:
            response = self._make_gpt_request(prompt, lyrics, line)
            # Parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "translation": line,
                    "interpretation": response,
                    "connectionsToContext": "Analysis could not be parsed into structured format."
                }
        except Exception as e:
            raise RuntimeError(f"Failed to generate analysis: {e}") from e

    def _create_analysis_prompt(self) -> str:
        """Create structured prompt for line analysis"""
        return """You are a poetic and lyrical interpreter with expertise in analyzing poetry and song lyrics. For each task, you will receive the full text of a song or poem as context and a specific line to analyze. Your task is to:
                        Translate the provided line into English while preserving its poetic essence and emotional depth.
                        Provide a deep and nuanced interpretation of the line, focusing on its themes, emotions, and significance.
                        Analyze the line in relation to the context of the full song or poem, explaining how it connects to broader themes and ideas.
                        Explore multiple layers of meaning (e.g., romantic, spiritual, philosophical, societal) in the interpretation.
                        Format your response as a valid JSON object.
                        Output Format
                        {
                          "translation": "[Translated line into English]",
                          "interpretation": "[Deep and nuanced interpretation of the line]",
                          "connectionsToContext": "[Explanation of how the line relates to the broader themes or context of the full song/poem]"
                        }

                        Additional Instructions
                        Context Awareness: Use the full text of the song/poem to enrich your interpretation of the specific line.
                        Preserve Depth: Ensure translations retain the emotional and lyrical depth of the original line.
                        Nuanced Analysis: Offer insights into symbolic, emotional, and thematic layers of the line.
                        Focus on the Specific Line: Your analysis should center on the given line, but draw from the broader context for clarity and depth.
                        Clarity: Avoid unnecessary repetition or generic statements."""

    def _create_theme_prompt(self, language_code: str) -> str:
        """Create appropriate theme prompt based on language"""
        prompts = {
            "en": "Briefly explain the main theme of this song in 2-3 sentences. Focus on the core message and emotions.",
            "hin": "इस गीत का मुख्य विषय 2-3 वाक्यों में संक्षेप में बताएं। मूल संदेश और भावनाओं पर ध्यान दें।",
            "urd": "اس گانے کا بنیادی موضوع 2-3 جملوں میں مختصر بیان کریں۔ بنیادی پیغام اور جذبات پر توجہ دیں۔"
        }
        return prompts.get(language_code, prompts["en"])

    def _make_gpt_request(self, prompt: str, lyrics: str, line: str) -> str:
        """Make request to GPT API"""
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Song lyrics: {lyrics}"},
        ]

        if line:
            messages.append(
                {"role": "user", "content": f"Analyze this specific line: {line}"})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                max_tokens=500,  # Increased for structured response
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}") from e

    def _make_theme_request(self, prompt: str, lyrics: str) -> str:
        """Make optimized request to GPT API for theme generation"""
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Song lyrics: {lyrics}"},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                max_tokens=150,  # Shorter for themes
                temperature=0.5  # More focused responses
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}") from e
