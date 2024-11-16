import streamlit as st
from browser_history.browsers import Chrome
import autogen

# Fetch Browser History
st.title("Mental Health Analysis via Search History")

st.write("This app analyzes your recent browsing history for potential mental health indicators.")

# Button to trigger history fetch
if st.button("Fetch and Analyze Browsing History"):
    st.write("Fetching your browsing history...")

    try:
        # Fetch history using the browser-history package
        f = Chrome()
        outputs = f.fetch_history()
        his = outputs.histories

        # Display fetched history
        st.write("Fetched Browsing History (First 10):")
    
        for h in his[:10]:
            st.write(f"{h[0]} - {h[1]}")

        # Define LLM Configurations
        llm_config = {
            "timeout": 600,
            "cache_seed": 44,
            "config_list": autogen.config_list_from_json("OAI_CONFIG_LIST.json"),
            "temperature": 0,
        }

        # Define agents
        psy_analyzer = autogen.AssistantAgent(
            name="PsyAnalyzer",
            system_message="You are a psychological analysis agent. Analyze structured data for mental health indicators.",
            llm_config=llm_config,
        )
        ad_creator = autogen.AssistantAgent(
            name="AdCreator",
            system_message="You are an ad content generator. Create supportive and empathetic ads based on analysis results.",
            llm_config=llm_config,
        )
        ethics_guard = autogen.AssistantAgent(
            name="EthicsGuard",
            system_message="You are an ethical compliance agent. Review all processes and outputs for adherence to ethical and legal standards.",
            llm_config=llm_config,
        )
        assistant = autogen.ConversableAgent(
            name="Assistant",
            system_message="You are a helpful AI assistant. Return 'TERMINATE' when the task is done.",
            llm_config=llm_config,
        )
        num_agent = autogen.AssistantAgent(
            name="NumAgent",
            system_message="Please analyze the following text and estimate the likelihood (from 0% to 100%) that the user is experiencing clinical depression. Look for signs such as hopelessness, sadness, withdrawal, fatigue, anhedonia (loss of interest), cognitive symptoms (difficulty concentrating), and thoughts of death or self-harm. Assess the overall emotional tone and negative thought patterns in the text.",
            llm_config=llm_config,
        )
        user_proxy = autogen.UserProxyAgent(
            "user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            default_auto_reply="",
            is_termination_msg=lambda x: True,
        )

        # Create Group Chat
        group_chat = autogen.GroupChat(
            agents=[user_proxy, psy_analyzer, ad_creator, ethics_guard, num_agent, assistant],
            messages=[],
            max_round=15,
        )
        manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

        # Run analysis
        st.write("Running analysis on browsing history...")

        data = user_proxy.initiate_chat(
            manager,
            message=f"""
            Below is a sample dataset to use with the workflow. The dataset includes user chat logs and search history, structured as input for the workflow:
            {his[:10]}
            """,
        )

        # Display AI Results
        st.write("AI Analysis Results:")
        for message in data.chat_history:
            st.write(f"**Agent Name**: {message['name']}")
            st.write(f"**Role**: {message['role']}")
            st.write(f"**Content**: {message['content']}")
            st.write("-" * 50)

    except Exception as e:
        st.error(f"An error occurred: {e}")
