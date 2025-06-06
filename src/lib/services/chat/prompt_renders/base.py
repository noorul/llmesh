#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base Model

Placeholder class that has to be overwritten
"""

import abc
from typing import Optional
from pydantic import BaseModel, Field


class BasePromptRender(abc.ABC):
    """
    Base class for file rendering. This is an abstract class that needs to be extended.
    """

    class Config(BaseModel):
        """
        Base Configuration model for prompt manager settings.
        """
        type: str = Field(
            ...,
            description="Type of the render deployment."
        )

    class Result(BaseModel):
        """
        Base Results class.
        """
        status: str = Field(
            default="success",
            description="Status of the operation, e.g., 'success' or 'failure'"
        )
        error_message: Optional[str] = Field(
            None,
            description="Detailed error message if the operation failed"
        )
        content: Optional[str] = Field(
            None,
            description="Content generated from the template file and input parameters"
        )

    @abc.abstractmethod
    def render(self, template_string: str, **params: str) -> Result:
        """
        Render prompt from template.

        :param template: Template string.
        :param params: Additional parameters for loading the prompt.
        """

    @abc.abstractmethod
    def load(self, prompt_name: str, **params: str) -> Result:
        """
        Load prompt from file.

        :param prompt_name: The name of the prompt to load.
        :param params: Additional parameters for loading the prompt.
        """

    @abc.abstractmethod
    def save(self, prompt_name: str, content: str) -> Result:
        """
        Save prompt to file.

        :param prompt_name: The name of the prompt to save.
        :param content: The content to save.
        """
