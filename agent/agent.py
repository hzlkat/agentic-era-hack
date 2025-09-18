# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.agents import SequentialAgent
from agent.prompts import return_instructions_root, return_instruction_liability, return_instruction_questionnaire
from agent.connector_tools import get_google_drive_tool
from agent.connector_tools import get_google_doc_tool

google_doc_tool = get_google_doc_tool()
google_drive_tool = get_google_drive_tool()
# from agent.tools.doc_publisher import docs_batch_update


credentials, project_id = google.auth.default()
if not project_id:
    # Fallback if ADC does not return project_id
    print("⚠️ WARNING: google.auth.default() did not return a project_id.")
    project_id = "your-project-id"  # <-- set manually or raise exception

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

# Questionnaire Agent
questionnaire_agent= LlmAgent(
    name="questionnaire_agent",
    model = "gemini-2.5-pro",
    description="Answer standard questionnaires from the uploaded contract.",
    instruction = return_instruction_questionnaire(),
    output_key="questionnaire_answers",
)


# Liability Agent
liability_agent= LlmAgent(
    name="liability_agent",
    model = "gemini-2.5-pro",
    description="Answer liabiliy questions from the uploaded contract and trigger escalation levels.",
    instruction = return_instruction_liability(),
    output_key="liability_answers",
)

# Publisher Agent to Google Drive
publisher_agent= LlmAgent(
    name="publisher_agent",
    model = "gemini-2.5-pro",
    instruction = ("""
      Call tool `gdrv_POST_v3_files` with:
        {
          \"body\": {
            \"name\": \"Contract Analysis – Report\",
            \"mimeType\": \"application/vnd.google-apps.document\"
          }
        "}
        Do NOT return any output for the user! 
    """),
    tools=[google_drive_tool],
    output_key = "document_id",
)

# Writer Agent
writer_agent= LlmAgent(
    name="writer_agent",
    model = "gemini-2.5-pro",
    instruction = ("""
    Compose the report from:
    - Questionnaire: {questionnaire_answers}
    - Liability: {liability_answers}
    and write it into the freshly created document using the {document_id}.
    CALL exactly one tool: google_doc_tool to do that.
    Do NOT OUTPUT ANY TEXT! ONLY after the tool run return: "Awesome, that was a success ! :) "
    """),
    tools=[google_doc_tool],
    output_key = "publish_result",
)

# Contract Analysis Team (Sequential Agent)
contract_analysis_team = SequentialAgent(
    name="contract_analysis_team",
    description="Performs a multi-stage contract analysis by processing documents, retrieving relevant BGB information, and preparing a final analysis.", 
    sub_agents = [questionnaire_agent,
                  liability_agent,
                  publisher_agent,
                  writer_agent
                  ],
)

root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    description = "Greets the user and guides the user through the Contract Analysis Process.",
    instruction=return_instructions_root(),
    sub_agents=[contract_analysis_team],
)
