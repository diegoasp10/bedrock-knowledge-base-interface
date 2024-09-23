# type: ignore
# pylint: disable=E0401,C0114
# ------------------------------------------------------
# Streamlit
# Knowledge Bases for Amazon Bedrock and LangChain 🦜️🔗
# ------------------------------------------------------
import os
import logging
from typing import List, Dict
from operator import itemgetter

import boto3
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_aws import ChatBedrock
from langchain_aws import AmazonKnowledgeBasesRetriever
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# ------------------------------------------------------
# Log level

logging.getLogger().setLevel(logging.ERROR) # reduce log level

# ------------------------------------------------------
# Amazon Bedrock - settings

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)

MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"

model_kwargs =  {
    "max_tokens": 2048,
    "temperature": 0.0,
    "top_k": 250,
    "top_p": 1,
    "stop_sequences": ["\n\nHuman"],
}

# ------------------------------------------------------
# LangChain - RAG chain with chat history

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."
         "Answer the question based only on the following context:\n {context}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

# Amazon Bedrock - KnowledgeBase Retriever
retriever = AmazonKnowledgeBasesRetriever(
    knowledge_base_id=os.getenv("KNOWLEDGE_BASE_ID"), # 👈 Set your Knowledge base ID
    retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 4}},
)

model = ChatBedrock(
    client=bedrock_runtime,
    MODEL_ID=MODEL_ID,
    model_kwargs=model_kwargs,
)

chain = (
    RunnableParallel({
        "context": itemgetter("question") | retriever,
        "question": itemgetter("question"),
        "history": itemgetter("history"),
    })
    .assign(response = prompt | model | StrOutputParser())
    .pick(["response", "context"])
)

# Streamlit Chat Message History
history = StreamlitChatMessageHistory(key="chat_messages")

# Chain with History
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: history,
    input_messages_key="question",
    history_messages_key="history",
    output_messages_key="response",
)

# ------------------------------------------------------
# Pydantic data model and helper function for Citations

class Citation(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    page_content: str
    metadata: Dict

def extract_citations(response: List[Dict]) -> List[Citation]: # pylint: disable=W0621
    """_summary_

    Args:
        response (List[Dict]): _description_

    Returns:
        List[Citation]: _description_
    """
    return [Citation(page_content=doc.page_content, metadata=doc.metadata) for doc in response]

# ------------------------------------------------------
# S3 Presigned URL

def create_presigned_url(bucket_name: str, object_name: str, expiration: int = 300) -> str:
    """Generate a presigned URL to share an S3 object"""
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object', # pylint: disable=W0621
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except NoCredentialsError: # pylint: disable=E0602
        st.error("AWS credentials not available")
        return ""
    return response

def parse_s3_uri(uri: str) -> tuple:
    """Parse S3 URI to extract bucket and key"""
    parts = uri.replace("s3://", "").split("/")
    bucket = parts[0] # pylint: disable=W0621
    key = "/".join(parts[1:]) # pylint: disable=W0621
    return bucket, key

# ------------------------------------------------------
# Streamlit
import streamlit as st # pylint: disable=C0413,E0401

# Page title
st.set_page_config(page_title='Knowledge Bases for Amazon Bedrock and LangChain 🦜️🔗')

# Clear Chat History function
def clear_chat_history():
    """_summary_
    """
    history.clear()
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

with st.sidebar:
    st.title('Knowledge Bases for Amazon Bedrock and LangChain 🦜️🔗')
    streaming_on = st.toggle('Streaming')
    st.button('Clear Chat History', on_click=clear_chat_history)
    st.divider()
    st.write("History Logs")
    st.write(history.messages)

# Initialize session state for messages if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat Input - User Prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    config = {"configurable": {"session_id": "any"}}

    if streaming_on:
        # Chain - Stream
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = '' # pylint: disable=C0103
            for chunk in chain_with_history.stream(
                {"question" : prompt, "history" : history},
                config
            ):
                if 'response' in chunk:
                    full_response += chunk['response']
                    placeholder.markdown(full_response)
                else:
                    full_context = chunk['context']
            placeholder.markdown(full_response)
            # Citations with S3 pre-signed URL
            citations = extract_citations(full_context)
            with st.expander("Show source details >"):
                for citation in citations:
                    st.write("Page Content:", citation.page_content)
                    s3_uri = citation.metadata['location']['s3Location']['uri']
                    bucket, key = parse_s3_uri(s3_uri)
                    presigned_url = create_presigned_url(bucket, key)
                    if presigned_url:
                        st.markdown(f"Source: [{s3_uri}]({presigned_url})")
                    else:
                        st.write(f"Source: {s3_uri} (Presigned URL generation failed)")
                    st.write("Score:", citation.metadata['score'])
            # session_state append
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        # Chain - Invoke
        with st.chat_message("assistant"):
            response = chain_with_history.invoke(
                {"question" : prompt, "history" : history},
                config
            )
            st.write(response['response'])
            # Citations with S3 pre-signed URL
            citations = extract_citations(response['context'])
            with st.expander("Show source details >"):
                for citation in citations:
                    st.write("Page Content:", citation.page_content)
                    s3_uri = citation.metadata['location']['s3Location']['uri']
                    bucket, key = parse_s3_uri(s3_uri)
                    presigned_url = create_presigned_url(bucket, key)
                    if presigned_url:
                        st.markdown(f"Source: [{s3_uri}]({presigned_url})")
                    else:
                        st.write(f"Source: {s3_uri} (Presigned URL generation failed)")
                    st.write("Score:", citation.metadata['score'])
            # session_state append
            st.session_state.messages.append({"role": "assistant", "content": response['response']})
