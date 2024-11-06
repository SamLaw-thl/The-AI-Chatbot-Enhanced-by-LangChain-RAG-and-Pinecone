import streamlit as st
from src.utils import download_hugging_face_embeddings
from pinecone import Pinecone
from langchain.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain import PromptTemplate
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv
from src.prompt import *

# Load environment variables
load_dotenv()

# Load embeddings
embeddings = download_hugging_face_embeddings()

# Initializing the Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(host=os.getenv("PINECONE_HOST"))

# Loading Prompt Template
PROMPT = PromptTemplate(template=prompt_tempalate, input_variables=["context", "question"])
chain_type_kwargs = {"prompt": PROMPT}

# Loading LLM
llm = CTransformers(model="model/llama-2-7b-chat.ggmlv3.q4_0.bin",
                    model_type="llama",
                    config={'max_new_tokens': 512,
                            'temperature': 0.8})

# Retrieve knowledge from Pinecone
namespace = os.getenv("namespace")
index_name = os.getenv("index_name")

knowledge = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    namespace=namespace,
    embedding=embeddings
)

# Retrieval QA
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=knowledge.as_retriever(search_kwargs={'k': 2}),
    return_source_documents=True
)


# $streamlit run app.py
def main():
    st.title("Personal AI Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Type your message:"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get response from the QA system
        response = qa({"query": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response["result"])  # Access the result field correctly

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response["result"]})

if __name__ == "__main__":
    main()
