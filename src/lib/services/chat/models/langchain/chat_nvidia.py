#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LangChain Nvidia Model

This module allows you to:
- Initialize the Nvidia API environment variables
- Return the LangChain Nvidia model
- Invoke a Large Language Model (LLM) to process a prompt
"""

from __future__ import annotations
import os
from typing import Optional, Dict, Any, Iterator, AsyncIterator
from pydantic import Field
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from src.lib.core.log import Logger
from src.lib.services.chat.models.base import BaseChatModel
from src.lib.services.chat.models.error_handler import model_error_handler, stream_error_handler


logger = Logger().get_logger()


class LangChainChatNvidiaModel(BaseChatModel):
    """
    Class for LangChain ChatMistralAI Model.
    """

    class Config(BaseChatModel.Config):
        """
        Configuration for the Chat Model class.
        """
        seed: Optional[int] = Field(
            None,
            description="Seed for model randomness."
        )
        base_url: Optional[str] = Field(
            None,
            description="Endpoint for the model API."
        )
        max_tokens: Optional[int] = Field(
            None,
            description="Max number of tokens to return."
        )

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initialize the LangChainChatNvidiaModel with the given configuration.

        :param config: Configuration dictionary for the model.
        """
        self.config = LangChainChatNvidiaModel.Config(**config)
        self.result = LangChainChatNvidiaModel.Result()
        self.model = self._init_model()

    def _init_model(self) -> ChatNVIDIA:
        """
        Get the LangChain ChatNVIDIA model instance.

        :return: ChatNVIDIA model instance.
        """
        logger.debug("Selected LangChain ChatNVIDIA")
        os.environ["NVIDIA_API_KEY"] = self.config.api_key
        args = self._init_model_arguments()
        return ChatNVIDIA(**args)

    def _init_model_arguments(self) -> Dict[str, Any]:
        """
        Create arguments for initializing the ChatNVIDIA model.

        :return: Dictionary of arguments for ChatNVIDIA.
        """
        args = {"model": self.config.model_name}
        if self.config.temperature is not None:
            args["temperature"] = self.config.temperature
        if self.config.seed is not None:
            args["seed"] = self.config.seed
        if self.config.base_url is not None:
            args["base_url"] = self.config.base_url
        if self.config.max_tokens is not None:
            args["max_tokens"] = self.config.max_tokens
        return args

    def get_model(self) -> LangChainChatNvidiaModel.Result:
        """
        Return the LLM model instance.

        :return: Result object containing the model instance.
        """
        self.result.model = self.model
        if self.model:
            self.result.status = "success"
            logger.debug(f"Returned model '{self.config.model_name}'")
        else:
            self.result.status = "failure"
            logger.error("No model instance available")
        return self.result

    @model_error_handler("An error occurred while invoking LLM")
    def invoke(self, messages: Any) -> LangChainChatNvidiaModel.Result:
        """
        Invoke the LLM to process the given message.

        :param messages: Messages to be processed by the model.
        :return: Result object containing the generated content.
        """
        self.result.status = "success"
        response = self.model.invoke(messages)
        self.result.content = response.content
        self.result.metadata = response.response_metadata
        logger.debug(f"Generated response: {self.result.content}")
        return self.result

    @stream_error_handler("Streaming error")
    def stream(self, messages: Any) -> Iterator[str]:
        '''
        Synchronously stream the model response token by token.

        :param messages: Message list formatted for the model.
        :return: Iterator yielding response chunks.
        '''
        for chunk in self.model.stream(messages):
            yield chunk.content

    @model_error_handler("An error occurred while async invoking LLM")
    async def ainvoke(self, messages: Any) -> LangChainChatNvidiaModel.Result:
        '''
        Asynchronously invoke the model with a list of messages.

        :param messages: Message list formatted for the model.
        :return: Result object with content and metadata.
        '''
        self.result.status = "success"
        response = await self.model.ainvoke(messages)
        self.result.content = response.content
        self.result.metadata = response.response_metadata
        logger.debug(f"Async prompt generated: {self.result.content}")
        return self.result

    @stream_error_handler("Async streaming error")
    async def astream(self, messages: Any) -> AsyncIterator[str]:
        '''
        Asynchronously stream the model response token by token.

        :param messages: Message list formatted for the model.
        :return: Async iterator yielding response chunks.
        '''
        async for chunk in self.model.astream(messages):
            yield chunk.content
