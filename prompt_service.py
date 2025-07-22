"""
Enhanced prompt service for handling templated prompts with variables,
language localization, and validation.
"""

import json
import re
from typing import Dict, Any, Optional, List
from i18n import i18n


class PromptService:
    def __init__(self, prompts_file: str = 'prompts.json'):
        self.prompts_file = prompts_file
        self.prompts = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """Load prompts from JSON file."""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                self.prompts = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompts file {self.prompts_file} not found")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in prompts file: {e}")
    
    def get_prompt_info(self, prompt_id: str) -> Optional[Dict]:
        """Get complete prompt information including variables and metadata."""
        return self.prompts.get(prompt_id)
    
    def validate_variables(self, prompt_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fill variables for a prompt.
        Returns validated variables with defaults applied.
        """
        prompt_info = self.get_prompt_info(prompt_id)
        if not prompt_info:
            raise ValueError(f"Prompt '{prompt_id}' not found")
        
        prompt_variables = prompt_info.get('variables', {})
        validated_vars = {}
        
        # Check required variables and apply defaults
        for var_name, var_config in prompt_variables.items():
            if var_config.get('required', False) and var_name not in variables:
                raise ValueError(f"Required variable '{var_name}' is missing")
            
            # Use provided value or default
            value = variables.get(var_name, var_config.get('default'))
            
            # Validate options if specified
            if 'options' in var_config and value not in var_config['options']:
                raise ValueError(
                    f"Variable '{var_name}' must be one of {var_config['options']}, got '{value}'"
                )
            
            validated_vars[var_name] = value
        
        return validated_vars
    
    def render_prompt(self, prompt_id: str, variables: Dict[str, Any], 
                     locale: Optional[str] = None) -> str:
        """
        Render a prompt template with variables and language localization.
        
        Args:
            prompt_id: ID of the prompt to render
            variables: Variables to substitute in the template
            locale: Language locale for response (auto-detected if None)
        
        Returns:
            Rendered prompt string ready for LLM
        """
        prompt_info = self.get_prompt_info(prompt_id)
        if not prompt_info:
            raise ValueError(f"Prompt '{prompt_id}' not found")
        
        # Validate and get final variables
        final_variables = self.validate_variables(prompt_id, variables)
        
        # Auto-detect language if not provided
        if locale is None:
            locale = i18n.get_locale()
        
        # Add response language to variables
        language_names = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'pt': 'Portuguese',
            'it': 'Italian',
            'zh': 'Chinese',
            'ja': 'Japanese'
        }
        
        final_variables['response_language'] = language_names.get(locale, 'English')
        
        # Get template
        template = prompt_info.get('template', '')
        
        # Add localized instructions if available
        localized_instructions = prompt_info.get('localized_instructions', {})
        if locale in localized_instructions:
            template += f"\n\nAdditional instruction: {localized_instructions[locale]}"
        
        # Render template
        try:
            rendered_prompt = template.format(**final_variables)
        except KeyError as e:
            raise ValueError(f"Missing variable in template: {e}")
        
        return rendered_prompt
    
    def get_prompt_categories(self) -> List[str]:
        """Get all available prompt categories."""
        categories = set()
        for prompt_info in self.prompts.values():
            if isinstance(prompt_info, dict) and 'category' in prompt_info:
                categories.add(prompt_info['category'])
        return sorted(categories)
    
    def get_prompts_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all prompts in a specific category."""
        result = {}
        for prompt_id, prompt_info in self.prompts.items():
            if isinstance(prompt_info, dict) and prompt_info.get('category') == category:
                result[prompt_id] = prompt_info
        return result
    
    def get_prompt_schema(self, prompt_id: str) -> Dict:
        """Get JSON schema for prompt variables (useful for API documentation)."""
        prompt_info = self.get_prompt_info(prompt_id)
        if not prompt_info:
            raise ValueError(f"Prompt '{prompt_id}' not found")
        
        variables = prompt_info.get('variables', {})
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for var_name, var_config in variables.items():
            prop_schema = {
                "type": var_config.get('type', 'string'),
                "description": var_config.get('description', '')
            }
            
            if 'default' in var_config:
                prop_schema['default'] = var_config['default']
            
            if 'options' in var_config:
                prop_schema['enum'] = var_config['options']
            
            schema['properties'][var_name] = prop_schema
            
            if var_config.get('required', False):
                schema['required'].append(var_name)
        
        return schema


# Global instance
prompt_service = PromptService()


def render_prompt(prompt_id: str, variables: Dict[str, Any], 
                 locale: Optional[str] = None) -> str:
    """Convenience function to render a prompt."""
    return prompt_service.render_prompt(prompt_id, variables, locale)
