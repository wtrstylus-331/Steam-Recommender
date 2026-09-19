import os
from typing import Any, Generator

from openai import OpenAI
from dotenv import load_dotenv
from enum import Enum

class Models(Enum):
    """
    Enum class to declare GPT models
    """
    GPT_SOL_5_6 = "gpt-5.6-sol"
    GPT_TERRA_5_6 = "gpt-5.6-terra"
    GPT_LUNA_5_6 = "gpt-5.6-luna"

    GPT_PRO_5_5 = "gpt-5.5-pro"
    GPT_5_5 = "gpt-5.5"

    GPT_PRO_5_4 = "gpt-5.4-pro"
    GPT_5_4 = "gpt-5.4"
    GPT_MINI_5_4 = "gpt-5.4-mini"
    GPT_NANO_5_4 = "gpt-5.4-nano"


class OpenAIInstance:
    _instance: "OpenAIInstance" = None
    _api_key: str

    client: OpenAI
    model: str
    history: list

    def __new__(cls) -> "OpenAIInstance":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        load_dotenv()
        self._api_key = os.getenv("OPENAI_API_KEY")
        self.model = Models.GPT_LUNA_5_6.value

        if not self._api_key:
            print("No OpenAI API key found!")
            self.client = None
        else:
            self.client = OpenAI(api_key=self._api_key)

        self.history = []
        #self._set_developer_content()

    def refresh(self) -> None:
        load_dotenv()
        new = os.getenv("OPENAI_API_KEY")

        if new != self._api_key:
            self._api_key = new
            self.client = OpenAI(api_key=self._api_key)

    def get_api_key(self) -> str | None:
        return self._api_key

    def reset_history(self) -> None:
        """
        Clears the input context for the model, and
        re-appends the developer context for a new conversation.
        """
        self.history.clear()
        self._set_developer_content()

    def _set_developer_content(self) -> None:
        self.history.append(
            {
                "role": "developer",
                "content": [
                    {
                        "type": "input_text",
                        "text": "You are an assistant inside a Steam‑style game profile web app.\nYou help users explore their game library by spotting playtime trends and answering questions.\n\nTone: friendly, conversational, concise, technically accurate.\n\nBehavior:\nResponses must fit a chat UI; use short paragraphs.\nReference only game data provided by the user or backend.\nGive clear reasoning for insights or recommendations.\nSummarize patterns when asked about Steam data.\nAnswer off‑topic questions normally but keep the same tone.\nNever invent game data.\n\nTools/Info Sources:\nFor Steam‑related lookups, rely only on store.steampowered.com, steamcommunity.com, and steamdb.info.\nAsk for clarification when user intent is unclear.\n\nStyle:\nNatural, human‑like, helpful.\nAvoid robotic or overly formal phrasing.\nUse light formatting (lists, short sections) only when useful.\n\nGoal:\nProvide context‑aware, helpful responses that enhance the user’s experience in the game profile interface."
                    }
                ]
            }
        )

    def send_message(self, message: str) -> Generator[str, Any, None]:
        """
        Sends the <message> provided into OpenAI, and returns OpenAI's response.

        Both <message> and the final response are appended into the model's input
        for persisting the conversation history.

        Returns the response as a string, otherwise return None if the client
        is not initialized.
        """
        if not self.client:
            return None

        self.history.append({
            "role": "user",
            "content": [
                {"type": "input_text", "text": message}
            ]
        })

        current_response = self.client.responses.create(
            model=self.model,
            input=self.history,
            text={
                "format": {
                    "type": "text"
                },
                "verbosity": "medium"
            },
            reasoning={
                "effort": "medium",
                "mode": "standard",
                "summary": "auto"
            },
            tools=[
                {
                    "type": "web_search",
                    "user_location": {
                        "type": "approximate"
                    },
                    "search_context_size": "medium",
                    "filters": {
                        "allowed_domains": [
                            "steamdb.info",
                            "store.steampowered.com",
                            "steamcommunity.com"
                        ]
                    }
                }
            ],
            store=False,
            include=[
                "reasoning.encrypted_content",
                "web_search_call.action.sources"
            ],
            stream=True
        )

        assistant_response = ""

        for event in current_response:
            if event.type == "response.output_text.delta":
                token = event.delta
                assistant_response += token
                yield token

        self.history.append({
            "role": "assistant",
            "content": [
                {"type": "output_text", "text": assistant_response}
            ]
        })

        # assistant_response = current_response.output_text
        # self.history.append({
        #     "role": "assistant",
        #     "content": [
        #         {"type": "output_text", "text": assistant_response}
        #     ]
        # })

        #return assistant_response

        # response = client.responses.create(
        #     model="gpt-5.6-luna",
        #     input=[
        #         {
        #             "role": "developer",
        #             "content": [
        #                 {
        #                     "type": "input_text",
        #                     "text": "You are an AI assistant inside a Steam‑style game profile web app.\nYou help users explore their game library, understand play history, spot trends, and answer general questions.\n\nTone: friendly, conversational, concise, technically accurate.\n\nBehavior:\nResponses must fit a chat UI; use short paragraphs.\nReference only game data provided by the user or backend.\nGive clear reasoning for insights or recommendations.\nSummarize patterns when asked about Steam data.\nAnswer off‑topic questions normally but keep the same tone.\nNever invent game data.\n\nTools / Info Sources:\nFor Steam‑related lookups, rely only on store.steampowered.com, steamcommunity.com, and steamdb.info.\nAsk for clarification when user intent is unclear.\n\nStyle:\nNatural, human‑like, helpful.\nAvoid robotic or overly formal phrasing.\nUse light formatting (lists, short sections) only when useful.\n\nGoal:  \nProvide context‑aware, helpful responses that enhance the user’s experience in the game profile interface."
        #                 }
        #             ]
        #         }
        #     ],
        #     text={
        #         "format": {
        #             "type": "text"
        #         },
        #         "verbosity": "medium"
        #     },
        #     reasoning={
        #         "effort": "medium",
        #         "mode": "standard",
        #         "summary": "auto"
        #     },
        #     tools=[
        #         {
        #             "type": "web_search",
        #             "user_location": {
        #                 "type": "approximate"
        #             },
        #             "search_context_size": "medium",
        #             "filters": {
        #                 "allowed_domains": [
        #                     "steamdb.info",
        #                     "store.steampowered.com",
        #                     "steamcommunity.com"
        #                 ]
        #             }
        #         }
        #     ],
        #     store=False,
        #     include=[
        #         "reasoning.encrypted_content",
        #         "web_search_call.action.sources"
        #     ]
        # )
