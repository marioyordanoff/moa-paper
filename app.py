import copy
import json
import os
from typing import Iterable

import streamlit as st
from dotenv import load_dotenv
from moa.agent import MOAgent
from moa.agent.moa import ResponseChunk
from streamlit_ace import st_ace

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Default configuration
default_config = {
    "main_model": "llama3-70b-8192",
    "cycles": 3,
    "layer_agent_config": {},
}

layer_agent_config_def = {
    "layer_agent_1": {
        "system_prompt": "Think through your response step by step. {helper_response}",
        "model_name": "llama3-8b-8192",
    },
    "layer_agent_2": {
        "system_prompt": "Respond with a thought and then your response to the question. {helper_response}",
        "model_name": "gemma-7b-it",
        "temperature": 0.7,
    },
    "layer_agent_3": {
        "system_prompt": "You are an expert at logic and reasoning. Always take a logical approach to the answer. {helper_response}",
        "model_name": "llama3-8b-8192",
    },
}

# Recommended Configuration

rec_config = {"main_model": "llama3-70b-8192", "cycles": 2, "layer_agent_config": {}}

layer_agent_config_rec = {
    "layer_agent_1": {
        "system_prompt": "Think through your response step by step. {helper_response}",
        "model_name": "llama3-8b-8192",
        "temperature": 0.1,
    },
    "layer_agent_2": {
        "system_prompt": "Respond with a thought and then your response to the question. {helper_response}",
        "model_name": "llama3-8b-8192",
        "temperature": 0.2,
    },
    "layer_agent_3": {
        "system_prompt": "You are an expert at logic and reasoning. Always take a logical approach to the answer. {helper_response}",
        "model_name": "llama3-8b-8192",
        "temperature": 0.4,
    },
    "layer_agent_4": {
        "system_prompt": "You are an expert planner agent. Create a plan for how to answer the human's query. {helper_response}",
        "model_name": "mixtral-8x7b-32768",
        "temperature": 0.5,
    },
}


def stream_response(messages: Iterable[ResponseChunk]):
    layer_outputs = {}
    for message in messages:
        if message["response_type"] == "intermediate":
            layer = message["metadata"]["layer"]
            if layer not in layer_outputs:
                layer_outputs[layer] = []
            layer_outputs[layer].append(message["delta"])
        else:
            # Display accumulated layer outputs
            for layer, outputs in layer_outputs.items():
                st.write(f"Layer {layer}")
                cols = st.columns(len(outputs))
                for i, output in enumerate(outputs):
                    with cols[i]:
                        st.expander(label=f"Agent {i+1}", expanded=False).write(output)

            # Clear layer outputs for the next iteration
            layer_outputs = {}

            # Yield the main agent's output
            yield message["delta"]


def set_moa_agent(
    main_model: str = default_config["main_model"],
    cycles: int = default_config["cycles"],
    layer_agent_config: dict[dict[str, any]] = copy.deepcopy(layer_agent_config_def),
    main_model_temperature: float = 0.1,
    override: bool = False,
):
    if override or ("main_model" not in st.session_state):
        st.session_state.main_model = main_model
    else:
        if "main_model" not in st.session_state:
            st.session_state.main_model = main_model

    if override or ("cycles" not in st.session_state):
        st.session_state.cycles = cycles
    else:
        if "cycles" not in st.session_state:
            st.session_state.cycles = cycles

    if override or ("layer_agent_config" not in st.session_state):
        st.session_state.layer_agent_config = layer_agent_config
    else:
        if "layer_agent_config" not in st.session_state:
            st.session_state.layer_agent_config = layer_agent_config

    if override or ("main_temp" not in st.session_state):
        st.session_state.main_temp = main_model_temperature
    else:
        if "main_temp" not in st.session_state:
            st.session_state.main_temp = main_model_temperature

    cls_ly_conf = copy.deepcopy(st.session_state.layer_agent_config)

    if override or ("moa_agent" not in st.session_state):
        st.session_state.moa_agent = MOAgent.from_config(
            main_model=st.session_state.main_model,
            cycles=st.session_state.cycles,
            layer_agent_config=cls_ly_conf,
            temperature=st.session_state.main_temp,
        )

    del cls_ly_conf
    del layer_agent_config


st.set_page_config(
    page_title="MoA With Groq",
    layout="wide",
)
valid_model_names = [
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma-7b-it",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

set_moa_agent()

# Sidebar for configuration
with st.sidebar:
    # config_form = st.form("Agent Configuration", border=False)
    st.title("MOA Configuration")
    with st.form("Agent Configuration", border=False):
        if st.form_submit_button("Use Recommended Config"):
            try:
                set_moa_agent(
                    main_model=rec_config["main_model"],
                    cycles=rec_config["cycles"],
                    layer_agent_config=layer_agent_config_rec,
                    override=True,
                )
                st.session_state.messages = []
                st.success("Configuration updated successfully!")
            except json.JSONDecodeError:
                st.error(
                    "Invalid JSON in Layer Agent Configuration. Please check your input."
                )
            except Exception as e:
                st.error(f"Error updating configuration: {str(e)}")
        # Main model selection
        new_main_model = st.selectbox(
            "Select Main Model",
            options=valid_model_names,
            index=valid_model_names.index(st.session_state.main_model),
        )

        # Cycles input
        new_cycles = st.number_input(
            "Number of Layers", min_value=1, max_value=10, value=st.session_state.cycles
        )

        # Main Model Temperature
        main_temperature = st.number_input(
            label="Main Model Temperature",
            value=0.1,
            min_value=0.0,
            max_value=1.0,
            step=0.1,
        )

        # Layer agent configuration
        tooltip = "Agents in the layer agent configuration run in parallel _per cycle_. Each layer agent supports all initialization parameters of [Langchain's ChatGroq](https://api.python.langchain.com/en/latest/chat_models/langchain_groq.chat_models.ChatGroq.html) class as valid dictionary fields."
        st.markdown("Layer Agent Config", help=tooltip)
        new_layer_agent_config = st_ace(
            value=json.dumps(st.session_state.layer_agent_config, indent=2),
            language="json",
            placeholder="Layer Agent Configuration (JSON)",
            show_gutter=False,
            wrap=True,
            auto_update=True,
        )

        if st.form_submit_button("Update Configuration"):
            try:
                new_layer_config = json.loads(new_layer_agent_config)
                set_moa_agent(
                    main_model=new_main_model,
                    cycles=new_cycles,
                    layer_agent_config=new_layer_config,
                    main_model_temperature=main_temperature,
                    override=True,
                )
                st.session_state.messages = []
                st.success("Configuration updated successfully!")
            except json.JSONDecodeError:
                st.error(
                    "Invalid JSON in Layer Agent Configuration. Please check your input."
                )
            except Exception as e:
                st.error(f"Error updating configuration: {str(e)}")


# Main app layout
st.header("Mixture of Agents", anchor=False)
st.write(
    "A demo of the Mixture of Agents architecture proposed by Together AI, Powered by Groq LLMs."
)


# Display current configuration
with st.expander("Current MOA Configuration", expanded=False):
    st.markdown(f"**Main Model**: ``{st.session_state.main_model}``")
    st.markdown(f"**Main Model Temperature**: ``{st.session_state.main_temp:.1f}``")
    st.markdown(f"**Layers**: ``{st.session_state.cycles}``")
    st.markdown("**Layer Agents Config**:")
    new_layer_agent_config = st_ace(
        value=json.dumps(st.session_state.layer_agent_config, indent=2),
        language="json",
        placeholder="Layer Agent Configuration (JSON)",
        show_gutter=False,
        wrap=True,
        readonly=True,
        auto_update=True,
    )

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if query := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    moa_agent: MOAgent = st.session_state.moa_agent
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        ast_mess = stream_response(moa_agent.chat(query, output_format="json"))
        response = st.write_stream(ast_mess)

    st.session_state.messages.append({"role": "assistant", "content": response})
