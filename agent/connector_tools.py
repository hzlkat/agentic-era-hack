from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

def get_google_drive_tool():
    return ApplicationIntegrationToolset(
        project="qwiklabs-gcp-04-7f24da64fc1b",
        location="us-central1",
        connection="contract-to-drive",
        actions=["POST_files"],
        tool_name_prefix="gdrive_",
        tool_instructions="Use to create a new file."
    )

def get_google_doc_tool():
    return ApplicationIntegrationToolset(
        project="qwiklabs-gcp-04-7f24da64fc1b",
        location="us-central1",
        connection="contract-to-doc",
        actions=["POST_v1/documents/%7BdocumentId%7D%3AbatchUpdate"],
        tool_name_prefix="gdoc_",
        tool_instructions="Use to batchUpdate a Google Doc."
    )