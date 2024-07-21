<div align="center">
     <h2>Mixture-of-Agents Enhances Large Language Model Capabilities</h2>
</div>

![Alt text](https://cdn.prod.website-files.com/650c3b59079d92475f37b68f/6667deae5d7fb05ba4f86c1c_moa.png)
*Figure 1: Illustration of the Mixture-of-Agents Structure. This example showcases 4 MoA layers with 3 agents in each layer. The agents here can share the same model.*


## Table of Contents
1. [Introduction](#introduction)
2. [Key Features](#key-features)
3. [Installation](#installation)
4. [Credits](#credits)

## Introduction

Mixture-of-Agents (MoA) is a novel approach to enhance the capabilities of Large Language Models (LLMs). By leveraging a structured ensemble of specialized agents, MoA improves performance across various tasks while maintaining efficiency and scalability. 

This project is based on the research paper "Mixture-of-Agents: Enhancing Large Language Model Capabilities" by Yixuan Wang, Jiawei Han, and Chao Zhang.

## Key Features

- MoA aims to mitigate individual model
deficiencies and enhance overall response quality through collaborative synthesis.
-  MoA models achieves state-of-art performance on AlpacaEval 2.0, MT-Bench and FLASK, surpassing GPT-4 Omni.
- The Mixture-of-Agents method does not require any fine-tuning and only utilizes the interface of prompting and generation of LLMs.

## Installation

1. Clone the repository:

```
git clone https://github.com/marioyordanoff/moa-paper
cd moa-paper
```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   Create a `.env` file in the root directory and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```
4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Credits


- [Groq](https://groq.com/) - Model Inference
- [Lancghain](https://www.langchain.com/) - Orchestration
- [Streamlit](https://streamlit.io/) - GUI
