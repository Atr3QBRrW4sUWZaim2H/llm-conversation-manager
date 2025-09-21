---
title: Prompt Engineering Techniques
source: https://chatgpt.com/c/677cac22-7bd4-8003-a8c7-cab56f40a8fe
---

# Prompt Engineering Techniques

#### You:
<time datetime="2025-01-07T04:22:58.694Z" title="1/7/2025, 1:22:58 PM">13:22</time>

summarize:
Write

Sign in
Prompt Engineering for Unbeatable AI Agents
AI Applied

AI Applied
·

Follow
8 min read
·
Jul 9, 2024

Different Agents Same Techniques

I’ve built quiet a few different types of agents lately and it’s become quite clear to me that pretty much all really-really good agents (and I’m talking about the really good ones like GPT Pilot, GPT Engineer, Devin and even the Self Operating Computer) all use very similar prompting techniques to produce the kinds of cutting-edge results they do.

In this article we’ll take a look at the most crucial prompts that enable these agents to do the work they do in the fashion that they do.

There’s not point in taking a look at these techniques without some good examples, as such we will use a project that has recently blown me away called Claude Engineer. Chances are you already know about this agent, it’s really high quality and has the ability to create entire code bases on its own. It also happens to use pretty much all the prompting methods we are about to discuss and as such acts a good illustrative example.
Iterative Refinement Prompting

One of the most important methods of prompting for agents to allow them to perform iterative operation or intermediate-step problem solving.

The power of this lies in enabling the models to perform tasks by creating intermediary steps and gradually ticking off one step at a time.
The best method

There’s a lot of ways to perform iterative refinement, and not all of the produce the best results. For example in claude-engineer, a step by step outline is creating by the model at the start of the task in AUTOMODE, this is prompted using the following line;

    You are currently in automode!!!

    When in automode:
    1. Set clear, achievable goals for yourself based on the user’s request
    2. Work through these goals one by one, using the available tools as needed
    …

While this method is effective, it has one major shortcoming, particularly when it comes to long-ended tasks;

When performing tasks with numerous steps there is the possibility that the initial plan (located in the 3rd message of the conversation) leaves the token space of the model. When this happends the model becomes unable to proceed according to plan and starts to try and figure out the next sep based on its previous steps. When this happens it performs incorrect actiosn with an error rate that increases with increasing message count.

Using a static To Do List is a much more effective method to allow the agents to plan through longer muti-step tasks. The idea here is that we prompt the model to be able to create a to do list using certain functions, we then use these functions to save the to do list to an aray and feed this array into the model on every message. For example

    You are an engine planner, you evaluate the current state of the plan and make decisions on what should be done to achieve the desired final goal.

    You have access to the following functions:
    {
    “initialize_plan”: {
    “name”: “initialize_plan”,
    “description”: “Initializes the plan with a predefined list of plan items.”,
    “entry_point”: “initialize_plan”,
    “parameters”: [
    {
    “name”: “plan_items”,
    “type”: “list of dict”,
    “description”: “A list of dictionaries, each representing a plan step with keys for ‘action’, ‘details’, and optionally ‘comments’.”,
    “required”: true
    }…

The example above illustrates the use of a AI model to manage a plan that will keep track of the complete list of tasks the agent needs to perform. This list is fed to the models at every response and will clearly indicated the current steps the model is on and what the next steps should be.

This system of planning enables agents, to not only perform tasks the require multi-step processes but also extremely long tasks that can span 100s of steps.

If you’re reading this blog chances are you’re interested in building agent powered solutions. At AIA, we build agent solutions that power the most advanced applications, take a look at our services to see if there’s something we can do for you.
Identity Prompting

The very first technique we should at is tole role-based prompting. You might be familiar with this technique as it is usually used at the beginning of most chatbots.

This prompt primarily tells the model what to do and most people know this, but even more importantly, the prompt instructs the model on what it is.
Why it’s so powerful

The power in this prompt comes from it’s ability to summarize very complex model behavior in a very small space. For example, the prompt;

    You are very proficient in Turkish legal matter

This prompt produces a very complicated set of behaviors from the model that would otherwise take a lot of prompting to produce. The model is;

    Able to confidently give legal advice without worrying about the accuracy of it’s statements.
    Gives detailed advice to try and meet the definition “proficient”.
    Presents its ideas in a clear, direct and concise manner without behaving uncertain like ChatGPT tends to.
    etc

This identity-based prompting approach enables us to program a near endless collection of behaviours into the model that would have otherwise taken a significantly larger amount of token space and time to carefully test and develop.
Practical Application

As you can see, this example illustrates the use of identity prompting to produce desirable results from the model without going into listing each individual character. The use of the prompt gives the model confidence in its actions and also produces a whole string of other behaviors that would otherwise take up a lot of token space to manually outline to the model.

One important thing to note is the use of two identity prompts that actually contradict each other.

    You are Claude, an AI assistant powered by Anthropic’s Claude-3.5-Sonnet model.

And

    You are an exceptional software developer with vast knowledge across multiple programming languages, frameworks, and best practices.

The reason for this is one particular quirk with newer, more advanced models where their desire to closely align with the goals of the system prompt can sometimes lead them to present a false identity to the user.

For instance if the model was told that it is a software developer and user asked what it is, it would state that it’s a software developer. Alternatively, when both prompts are used, it will pick out the AI Model prompt and use that to reply the user’s question instead.
When to use this

Deciding on when to use an identity prompt is a little bit tricky but in some cases it comes naturally. For instance, right at the beginning of your prompt.

The more useful cases though, tend to come in a bit later on and can only be identified at the end of the prompting job. For example;

    You AVOID engaging in lengthy conversations that are not converning legal advice. IN THESE CASES YOU LET THE USER KNOW THAT YOU ARE ONLY HERE TO PROVIDE LEGAL HELP AND NOTHING ELSE AND POLITELY DECLINE TO PROCEED BUT ASK IF THERE IS ANY ABOUT THE LAW THEY NEED HELP WITH.

    If you think additional information on the matter can help you provide better assistance, towards the end of your response, you can ask the user for the specific details which might help you better evaluate their situation.

This prompt instructs the model on two main ideas, not discussing non-law issues and also asking for addition information if though necessary. It does so in 495 character and 101 tokens.

Because these are subjective concepts where the model needs to make a decision about what the right thing to do is, we can better convey these ideas using identity prompts.

    You are a very straight lawyer and are never interested in discussing non-law issues, you politely communicate this to users who ask unrelated questions.

    You are always interested in solving the user’s entire problem, because of this you ask for additional information to provide more appropriate solutions.

This prompt produces slightly better results and does so in 1/3 the number of tokens.
Self-reflection Prompts

One of the more advanced techniques in prompt engineering is the use of self-reflection prompts. This method enables AI agents to evaluate their own output based on introspection. I first this being extensively used in the Self Operating Computer project back in the day, this allowed GPT 4 turbo to evaluate the result of its actions at the end of its operation.
Why it’s so powerful

Self-reflection prompts allows agents consider the efficacy of their previous actions to see if they match the desired outcomes. This not only improves the current task but also helps in learning from mistakes, thus refining future responses. For example, consider the prompt:

“Once you have finished the described task. Evaluate the outcome to see if it fully matches the user’s goal as described in the original prompt.”

This prompt encourages the model to:

    Review its own output critically.
    Identify any gaps or inaccuracies in the response.
    Make necessary corrections or enhancements to ensure completeness and accuracy.

When to use this

Self reflection prompting is particularly difficult because it might lead the model into an endless loop. If the model is trying to be too perfect, it might try to continuously improve its work and never finish.

To overcome this, when instructing the model to evaluate its output you must use clear concise goals such as ;

    If all requirements are matched
    All items have been processed
    etc

The goal here is to remove the need for the model to subjectively have to decide when to stop. Other than that all you’ll need to do is set the model up in an infinite loop and let it run free.

That’ll be all for today, if you’re interested in taking a look at more of our content from the blog be sure to check out https://blog.aiappliedsuite.com/
Sign up to discover human stories that deepen your understanding of the world.
Free

Distraction-free reading. No ads.

Organize your knowledge with lists and highlights.

Tell your story. Find your audience.
Membership

Read member-only stories

Support writers you read most

Earn money for your writing

Listen to audio narrations

Read offline with the Medium app
Ai Agents
Agents
Artificial Intelligence
AI

AI Applied
Written by AI Applied
72 Followers
·
10 Following

aiappliedsuite.com
No responses yet

What are your thoughts?

Also publish to my profile
More from AI Applied
Create a Modern 3D Shopping Website | threejs | For Beginners
The Startup

In

The Startup

by

AI Applied
Create a Modern 3D Shopping Website | threejs | For Beginners
Let’s take websites to the next level together. In this post I explore (with you, hopefully) the endless possibilities of 3D websites.
Feb 18, 2021
140
1
Practical Introduction to Jupyter Notebooks— 1. Installation, Setup, and Data Handling
AI Applied

AI Applied
Practical Introduction to Jupyter Notebooks— 1. Installation, Setup, and Data Handling
Jupyter is basically the home of any Data Scientist, we can do amazing simple things in it and also some rather complex things.
Sep 23, 2023
Comment utiliser GitHub CLI — La nouvelle interface de ligne de commande GitHub — | Namu
AI Applied

AI Applied
Comment utiliser GitHub CLI — La nouvelle interface de ligne de commande GitHub — | Namu
GitHub CLI est GitHub sur la ligne de commande. Il apporte des demandes d’attraction, des problèmes et d’autres concepts GitHub au…
Oct 18, 2020
How to Use GitHub CLI — The New GitHub Command-Line Interface
The Startup

In

The Startup

by

AI Applied
How to Use GitHub CLI — The New GitHub Command-Line Interface
Complete guide to getting used to the new GitHub CLIm with fancy tools and features I’m sure this is gonna be a great addition to your…
Oct 7, 2020
84
See all from AI Applied
Recommended from Medium
Master Agentic AI: A Beginner’s Step-by-Step Guide with SuperAgentX — Tutorial Series (Part 1)
Prabhu Raghav

Prabhu Raghav
Master Agentic AI: A Beginner’s Step-by-Step Guide with SuperAgentX — Tutorial Series (Part 1)
Hello Everyone, Welcome to the Agent AI Tutorial Series — Part 1! 🚀
Nov 20, 2024
227
1
Agentic AI: Build a Tech Research Agent
Level Up Coding

In

Level Up Coding

by

Ida Silfverskiöld
Agentic AI: Build a Tech Research Agent
Using a custom data pipeline with millions of texts
Sep 5, 2024
988
14
Lists
Generative AI Recommended Reading
52 stories·1588 saves
A phone with a tweet on it describing a deepfake video of the Ukrainian president, with a labeled fake image in the background
AI Regulation
6 stories·668 saves
What is ChatGPT?
9 stories·491 saves
ChatGPT prompts
51 stories·2432 saves
Stateful and Responsible AI Agents
AI Advances

In

AI Advances

by

Debmalya Biswas
Stateful and Responsible AI Agents
Integrating AgentOps Monitoring with Responsible AI Practices
Aug 27, 2024
306
1
Build Your LLM Engineer Portfolio: A 3-Month Roadmap
Towards AI

In

Towards AI

by

Maxime Jabarian
Build Your LLM Engineer Portfolio: A 3-Month Roadmap
A step-by-step guide to designing, refining, and showcasing a portfolio that kickstarts your career.
Dec 14, 2024
757
2
Choosing the Right AI Agent Framework: LangGraph vs CrewAI vs OpenAI Swarm
Relari Blog

In

Relari Blog

by

Yi Zhang
Choosing the Right AI Agent Framework: LangGraph vs CrewAI vs OpenAI Swarm
In-depth comparison of agent orchestration with the same Agentic Finance App built using 3 different frameworks.
Dec 2, 2024
513
10
How to Build AI Agents from Scratch with Python
Samar Singh

Samar Singh
How to Build AI Agents from Scratch with Python
Introduction to AI Agents
Aug 27, 2024
30
See more recommendations

Help

Status

About

Careers

Press

Blog

Privacy

Terms

Text to speech

Teams


#### ChatGPT:
<time datetime="2025-01-07T04:23:03.134Z" title="1/7/2025, 1:23:03 PM">13:23</time>

**Summary of "Prompt Engineering for Unbeatable AI Agents" by AI Applied**

In the article "Prompt Engineering for Unbeatable AI Agents," AI Applied explores the common prompting techniques used by top-performing AI agents such as GPT Pilot, GPT Engineer, Devin, and the Self Operating Computer. The author emphasizes that these agents achieve their exceptional results through similar sophisticated prompting strategies.

**Key Techniques Discussed:**

1. **Iterative Refinement Prompting:**
   - **Purpose:** Enables AI agents to handle multi-step and complex tasks by breaking them down into manageable intermediary steps.
   - **Method:** Instead of a simple step-by-step outline, which can become cumbersome for long tasks, a static To Do list is maintained. This list is managed using specific functions that store and update tasks, ensuring the agent can efficiently handle tasks with hundreds of steps without exceeding token limits.
   - **Example:** The Claude Engineer agent uses functions like `initialize_plan` to create and manage a dynamic list of tasks, allowing continuous progress without losing track of the overall plan.

2. **Identity Prompting:**
   - **Purpose:** Defines the role and expertise of the AI model succinctly to guide its behavior and responses.
   - **Power:** A concise identity prompt can encapsulate complex behaviors, enabling the model to perform specialized tasks effectively without extensive additional instructions.
   - **Example:**
     - "You are very proficient in Turkish legal matters."
     - Combining multiple identity prompts, such as defining the model as both an AI assistant and a software developer, helps manage its responses more accurately.
   - **Application:** Useful at the beginning of interactions or when specific behaviors are required, such as limiting discussions to legal advice or seeking additional information to enhance responses.

3. **Self-Reflection Prompts:**
   - **Purpose:** Allows AI agents to evaluate and improve their own outputs through introspection.
   - **Power:** Enhances the accuracy and completeness of responses by encouraging the model to identify and correct its own mistakes.
   - **Method:** After completing a task, the model assesses whether the outcome meets the user’s goals and makes necessary adjustments.
   - **Challenge:** Risk of creating an endless loop of self-improvement. This is mitigated by setting clear, concise goals for evaluation, ensuring the process remains finite and focused.
   - **Example:** "Once you have finished the described task, evaluate the outcome to see if it fully matches the user’s goal as described in the original prompt."

**Conclusion:**
The article highlights that effective prompt engineering is crucial for developing advanced AI agents capable of handling complex and lengthy tasks. By utilizing techniques like iterative refinement, identity prompting, and self-reflection, developers can create AI agents that perform reliably and efficiently. AI Applied also offers services to help build such agent-powered solutions, encouraging readers to explore their offerings for advanced AI applications.

For more insights and detailed discussions, visit the [AI Applied blog](https://blog.aiappliedsuite.com/).


#### You:
<time datetime="2025-01-07T04:24:40.707Z" title="1/7/2025, 1:24:40 PM">13:24</time>

Continue by summarizing:
```

Hugging Face's logo Hugging Face

Models
Datasets
Spaces
Posts
Docs
Enterprise
Pricing

    Log In
    Sign Up

Transformers
137,240
Get started
🤗 Transformers
Quick tour
Installation
Adding a new model to `transformers`
Tutorials
Run inference with pipelines
Write portable code with AutoClass
Preprocess data
Fine-tune a pretrained model
Train with a script
Set up distributed training with 🤗 Accelerate
Load and train adapters with 🤗 PEFT
Share your model
Agents 101
Agents, supercharged - Multi-agents, External tools, and more
Generation with LLMs
Chatting with Transformers
Task Guides
Natural Language Processing
Audio
Computer Vision
Multimodal
Generation
Prompting
Image tasks with IDEFICS
LLM prompting guide
Developer guides
Use fast tokenizers from 🤗 Tokenizers
Run inference with multilingual models
Use model-specific APIs
Share a custom model
Chat templates
Trainer
Run training on Amazon SageMaker
Export to ONNX
Export to TFLite
Export to TorchScript
Benchmarks
Notebooks with examples
Community resources
Troubleshoot
Interoperability with GGUF files
Interoperability with TikToken files
Modularity in `transformers`
Model Hacking (overwriting a class to your usage)
Quantization Methods
Getting started
bitsandbytes
GPTQ
AWQ
AQLM
Quanto
EETQ
HQQ
FBGEMM_FP8
Optimum
TorchAO
BitNet
compressed-tensors
Contribute new quantization method
Performance and scalability
Overview
LLM inference optimization
Efficient training techniques
Methods and tools for efficient training on a single GPU
Multiple GPUs and parallelism
Fully Sharded Data Parallel
DeepSpeed
Efficient training on CPU
Distributed CPU training
Training on TPU with TensorFlow
PyTorch training on Apple silicon
Custom hardware for training
Hyperparameter Search using Trainer API
Optimizing inference
CPU inference
GPU inference
Multi-GPU inference
Instantiate a big model
Debugging
XLA Integration for TensorFlow Models
Optimize inference using `torch.compile()`
Contribute
How to contribute to 🤗 Transformers?
How to add a model to 🤗 Transformers?
How to add a pipeline to 🤗 Transformers?
Testing
Checks on a Pull Request
Conceptual guides
Philosophy
Glossary
What 🤗 Transformers can do
How 🤗 Transformers solve tasks
The Transformer model family
Summary of the tokenizers
Attention mechanisms
Padding and truncation
BERTology
Perplexity of fixed-length models
Pipelines for webserver inference
Model training anatomy
Getting the most out of LLMs
API
Main Classes
Agents and Tools
Auto Classes
Backbones
Callbacks
Configuration
Data Collator
Keras callbacks
Logging
Models
Text Generation
ONNX
Optimization
Model outputs
Pipelines
Processors
Quantization
Tokenizer
Trainer
DeepSpeed
ExecuTorch
Feature Extractor
Image Processor
Models
Text models
Vision models
Audio models
Video models
Multimodal models
Reinforcement learning models
Time series models
Graph models
Internal Helpers
Custom Layers and Utilities
Utilities for pipelines
Utilities for Tokenizers
Utilities for Trainer
Utilities for Generation
Utilities for Image Processors
Utilities for Audio processing
General Utilities
Utilities for Time Series
Join the Hugging Face community

and get access to the augmented documentation experience
Collaborate on models, datasets and Spaces
Faster examples with accelerated inference
Switch between documentation themes

to get started

LLM prompting guide

Large Language Models such as Falcon, LLaMA, etc. are pretrained transformer models initially trained to predict the next token given some input text. They typically have billions of parameters and have been trained on trillions of tokens for an extended period of time. As a result, these models become quite powerful and versatile, and you can use them to solve multiple NLP tasks out of the box by instructing the models with natural language prompts.

Designing such prompts to ensure the optimal output is often called “prompt engineering”. Prompt engineering is an iterative process that requires a fair amount of experimentation. Natural languages are much more flexible and expressive than programming languages, however, they can also introduce some ambiguity. At the same time, prompts in natural language are quite sensitive to changes. Even minor modifications in prompts can lead to wildly different outputs.

While there is no exact recipe for creating prompts to match all cases, researchers have worked out a number of best practices that help to achieve optimal results more consistently.

This guide covers the prompt engineering best practices to help you craft better LLM prompts and solve various NLP tasks. You’ll learn:

    Basics of prompting
    Best practices of LLM prompting
    Advanced prompting techniques: few-shot prompting and chain-of-thought
    When to fine-tune instead of prompting

Prompt engineering is only a part of the LLM output optimization process. Another essential component is choosing the optimal text generation strategy. You can customize how your LLM selects each of the subsequent tokens when generating the text without modifying any of the trainable parameters. By tweaking the text generation parameters, you can reduce repetition in the generated text and make it more coherent and human-sounding. Text generation strategies and parameters are out of scope for this guide, but you can learn more about these topics in the following guides:

    Generation with LLMs
    Text generation strategies

Basics of prompting
Types of models

The majority of modern LLMs are decoder-only transformers. Some examples include: LLaMA, Llama2, Falcon, GPT2. However, you may encounter encoder-decoder transformer LLMs as well, for instance, Flan-T5 and BART.

Encoder-decoder-style models are typically used in generative tasks where the output heavily relies on the input, for example, in translation and summarization. The decoder-only models are used for all other types of generative tasks.

When using a pipeline to generate text with an LLM, it’s important to know what type of LLM you are using, because they use different pipelines.

Run inference with decoder-only models with the text-generation pipeline:

from transformers import pipeline

import torch

torch.manual_seed(0)

generator = pipeline('text-generation', model = 'openai-community/gpt2')

prompt = "Hello, I'm a language model"

generator(prompt, max_length = 30)
[{'generated_text': "Hello, I'm a language model programmer so you can use some of my stuff. But you also need some sort of a C program to run."}]

To run inference with an encoder-decoder, use the text2text-generation pipeline:

text2text_generator = pipeline("text2text-generation", model = 'google/flan-t5-base')

prompt = "Translate from English to French: I'm very happy to see you"

text2text_generator(prompt)
[{'generated_text': 'Je suis très heureuse de vous rencontrer.'}]

Base vs instruct/chat models

Most of the recent LLM checkpoints available on 🤗 Hub come in two versions: base and instruct (or chat). For example, tiiuae/falcon-7b and tiiuae/falcon-7b-instruct.

Base models are excellent at completing the text when given an initial prompt, however, they are not ideal for NLP tasks where they need to follow instructions, or for conversational use. This is where the instruct (chat) versions come in. These checkpoints are the result of further fine-tuning of the pre-trained base versions on instructions and conversational data. This additional fine-tuning makes them a better choice for many NLP tasks.

Let’s illustrate some simple prompts that you can use with tiiuae/falcon-7b-instruct to solve some common NLP tasks.
NLP tasks

First, let’s set up the environment:

pip install -q transformers accelerate

Next, let’s load the model with the appropriate pipeline ("text-generation"):

from transformers import pipeline, AutoTokenizer

import torch

torch.manual_seed(0)

model = "tiiuae/falcon-7b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model)

pipe = pipeline(

    "text-generation",

    model=model,

    tokenizer=tokenizer,

    torch_dtype=torch.bfloat16,

    device_map="auto",

)

Note that Falcon models were trained using the bfloat16 datatype, so we recommend you use the same. This requires a recent version of CUDA and works best on modern cards.

Now that we have the model loaded via the pipeline, let’s explore how you can use prompts to solve NLP tasks.
Text classification

One of the most common forms of text classification is sentiment analysis, which assigns a label like “positive”, “negative”, or “neutral” to a sequence of text. Let’s write a prompt that instructs the model to classify a given text (a movie review). We’ll start by giving the instruction, and then specifying the text to classify. Note that instead of leaving it at that, we’re also adding the beginning of the response - "Sentiment: ":

torch.manual_seed(0)

prompt = """Classify the text into neutral, negative or positive. 

Text: This movie is definitely one of my favorite movies of its kind. The interaction between respectable and morally strong characters is an ode to chivalry and the honor code amongst thieves and policemen.

Sentiment:

"""

sequences = pipe(

    prompt,

    max_new_tokens=10,

)

for seq in sequences:

    print(f"Result: {seq['generated_text']}")
Result: Classify the text into neutral, negative or positive. 
Text: This movie is definitely one of my favorite movies of its kind. The interaction between respectable and morally strong characters is an ode to chivalry and the honor code amongst thieves and policemen.
Sentiment:
Positive

As a result, the output contains a classification label from the list we have provided in the instructions, and it is a correct one!

You may notice that in addition to the prompt, we pass a max_new_tokens parameter. It controls the number of tokens the model shall generate, and it is one of the many text generation parameters that you can learn about in Text generation strategies guide.
Named Entity Recognition

Named Entity Recognition (NER) is a task of finding named entities in a piece of text, such as a person, location, or organization. Let’s modify the instructions in the prompt to make the LLM perform this task. Here, let’s also set return_full_text = False so that output doesn’t contain the prompt:

torch.manual_seed(1)

prompt = """Return a list of named entities in the text.

Text: The Golden State Warriors are an American professional basketball team based in San Francisco.

Named entities:

"""

sequences = pipe(

    prompt,

    max_new_tokens=15,

    return_full_text = False,    

)

for seq in sequences:

    print(f"{seq['generated_text']}")
- Golden State Warriors
- San Francisco

As you can see, the model correctly identified two named entities from the given text.
Translation

Another task LLMs can perform is translation. You can choose to use encoder-decoder models for this task, however, here, for the simplicity of the examples, we’ll keep using Falcon-7b-instruct, which does a decent job. Once again, here’s how you can write a basic prompt to instruct a model to translate a piece of text from English to Italian:

torch.manual_seed(2)

prompt = """Translate the English text to Italian.

Text: Sometimes, I've believed as many as six impossible things before breakfast.

Translation:

"""

sequences = pipe(

    prompt,

    max_new_tokens=20,

    do_sample=True,

    top_k=10,

    return_full_text = False,

)

for seq in sequences:

    print(f"{seq['generated_text']}")
A volte, ho creduto a sei impossibili cose prima di colazione.

Here we’ve added a do_sample=True and top_k=10 to allow the model to be a bit more flexible when generating output.
Text summarization

Similar to the translation, text summarization is another generative task where the output heavily relies on the input, and encoder-decoder models can be a better choice. However, decoder-style models can be used for this task as well. Previously, we have placed the instructions at the very beginning of the prompt. However, the very end of the prompt can also be a suitable location for instructions. Typically, it’s better to place the instruction on one of the extreme ends.

torch.manual_seed(3)

prompt = """Permaculture is a design process mimicking the diversity, functionality and resilience of natural ecosystems. The principles and practices are drawn from traditional ecological knowledge of indigenous cultures combined with modern scientific understanding and technological innovations. Permaculture design provides a framework helping individuals and communities develop innovative, creative and effective strategies for meeting basic needs while preparing for and mitigating the projected impacts of climate change.

Write a summary of the above text.

Summary:

"""

sequences = pipe(

    prompt,

    max_new_tokens=30,

    do_sample=True,

    top_k=10,

    return_full_text = False,

)

for seq in sequences:

    print(f"{seq['generated_text']}")
Permaculture is an ecological design mimicking natural ecosystems to meet basic needs and prepare for climate change. It is based on traditional knowledge and scientific understanding.

Question answering

For question answering task we can structure the prompt into the following logical components: instructions, context, question, and the leading word or phrase ("Answer:") to nudge the model to start generating the answer:

torch.manual_seed(4)

prompt = """Answer the question using the context below.

Context: Gazpacho is a cold soup and drink made of raw, blended vegetables. Most gazpacho includes stale bread, tomato, cucumbers, onion, bell peppers, garlic, olive oil, wine vinegar, water, and salt. Northern recipes often include cumin and/or pimentón (smoked sweet paprika). Traditionally, gazpacho was made by pounding the vegetables in a mortar with a pestle; this more laborious method is still sometimes used as it helps keep the gazpacho cool and avoids the foam and silky consistency of smoothie versions made in blenders or food processors.

Question: What modern tool is used to make gazpacho?

Answer:

"""

sequences = pipe(

    prompt,

    max_new_tokens=10,

    do_sample=True,

    top_k=10,

    return_full_text = False,

)

for seq in sequences:

    print(f"Result: {seq['generated_text']}")
Result: Modern tools often used to make gazpacho include

Reasoning

Reasoning is one of the most difficult tasks for LLMs, and achieving good results often requires applying advanced prompting techniques, like Chain-of-thought.

Let’s try if we can make a model reason about a simple arithmetics task with a basic prompt:

torch.manual_seed(5)

prompt = """There are 5 groups of students in the class. Each group has 4 students. How many students are there in the class?"""

sequences = pipe(

    prompt,

    max_new_tokens=30,

    do_sample=True,

    top_k=10,

    return_full_text = False,

)

for seq in sequences:

    print(f"Result: {seq['generated_text']}")
Result: 
There are a total of 5 groups, so there are 5 x 4=20 students in the class.

Correct! Let’s increase the complexity a little and see if we can still get away with a basic prompt:

torch.manual_seed(6)

prompt = """I baked 15 muffins. I ate 2 muffins and gave 5 muffins to a neighbor. My partner then bought 6 more muffins and ate 2. How many muffins do we now have?"""

sequences = pipe(

    prompt,

    max_new_tokens=10,

    do_sample=True,

    top_k=10,

    return_full_text = False,

)

for seq in sequences:

    print(f"Result: {seq['generated_text']}")
Result: 
The total number of muffins now is 21

This is a wrong answer, it should be 12. In this case, this can be due to the prompt being too basic, or due to the choice of model, after all we’ve picked the smallest version of Falcon. Reasoning is difficult for models of all sizes, but larger models are likely to perform better.
Best practices of LLM prompting

In this section of the guide we have compiled a list of best practices that tend to improve the prompt results:

    When choosing the model to work with, the latest and most capable models are likely to perform better.
    Start with a simple and short prompt, and iterate from there.
    Put the instructions at the beginning of the prompt, or at the very end. When working with large context, models apply various optimizations to prevent Attention complexity from scaling quadratically. This may make a model more attentive to the beginning or end of a prompt than the middle.
    Clearly separate instructions from the text they apply to - more on this in the next section.
    Be specific and descriptive about the task and the desired outcome - its format, length, style, language, etc.
    Avoid ambiguous descriptions and instructions.
    Favor instructions that say “what to do” instead of those that say “what not to do”.
    “Lead” the output in the right direction by writing the first word (or even begin the first sentence for the model).
    Use advanced techniques like Few-shot prompting and Chain-of-thought
    Test your prompts with different models to assess their robustness.
    Version and track the performance of your prompts.

Advanced prompting techniques
Few-shot prompting

The basic prompts in the sections above are the examples of “zero-shot” prompts, meaning, the model has been given instructions and context, but no examples with solutions. LLMs that have been fine-tuned on instruction datasets, generally perform well on such “zero-shot” tasks. However, you may find that your task has more complexity or nuance, and, perhaps, you have some requirements for the output that the model doesn’t catch on just from the instructions. In this case, you can try the technique called few-shot prompting.

In few-shot prompting, we provide examples in the prompt giving the model more context to improve the performance. The examples condition the model to generate the output following the patterns in the examples.

Here’s an example:

torch.manual_seed(0)

prompt = """Text: The first human went into space and orbited the Earth on April 12, 1961.

Date: 04/12/1961

Text: The first-ever televised presidential debate in the United States took place on September 28, 1960, between presidential candidates John F. Kennedy and Richard Nixon. 

Date:"""

sequences = pipe(

    prompt,

    max_new_tokens=8,

    do_sample=True,

    top_k=10,

)

for seq in sequences:

    print(f"Result: {seq['generated_text']}")
Result: Text: The first human went into space and orbited the Earth on April 12, 1961.
Date: 04/12/1961
Text: The first-ever televised presidential debate in the United States took place on September 28, 1960, between presidential candidates John F. Kennedy and Richard Nixon. 
Date: 09/28/1960

In the above code snippet we used a single example to demonstrate the desired output to the model, so this can be called a “one-shot” prompting. However, depending on the task complexity you may need to use more than one example.

Limitations of the few-shot prompting technique:

    While LLMs can pick up on the patterns in the examples, these technique doesn’t work well on complex reasoning tasks
    Few-shot prompting requires creating lengthy prompts. Prompts with large number of tokens can increase computation and latency. There’s also a limit to the length of the prompts.
    Sometimes when given a number of examples, models can learn patterns that you didn’t intend them to learn, e.g. that the third movie review is always negative.

Chain-of-thought

Chain-of-thought (CoT) prompting is a technique that nudges a model to produce intermediate reasoning steps thus improving the results on complex reasoning tasks.

There are two ways of steering a model to producing the reasoning steps:

    few-shot prompting by illustrating examples with detailed answers to questions, showing the model how to work through a problem.
    by instructing the model to reason by adding phrases like “Let’s think step by step” or “Take a deep breath and work through the problem step by step.”

If we apply the CoT technique to the muffins example from the reasoning section and use a larger model, such as (tiiuae/falcon-180B-chat) which you can play with in the HuggingChat, we’ll get a significant improvement on the reasoning result:

Let's go through this step-by-step:
1. You start with 15 muffins.
2. You eat 2 muffins, leaving you with 13 muffins.
3. You give 5 muffins to your neighbor, leaving you with 8 muffins.
4. Your partner buys 6 more muffins, bringing the total number of muffins to 14.
5. Your partner eats 2 muffins, leaving you with 12 muffins.
Therefore, you now have 12 muffins.

Prompting vs fine-tuning

You can achieve great results by optimizing your prompts, however, you may still ponder whether fine-tuning a model would work better for your case. Here are some scenarios when fine-tuning a smaller model may be a preferred option:

    Your domain is wildly different from what LLMs were pre-trained on and extensive prompt optimization did not yield sufficient results.
    You need your model to work well in a low-resource language.
    You need the model to be trained on sensitive data that is under strict regulations.
    You have to use a small model due to cost, privacy, infrastructure or other limitations.

In all of the above examples, you will need to make sure that you either already have or can easily obtain a large enough domain-specific dataset at a reasonable cost to fine-tune a model. You will also need to have enough time and resources to fine-tune a model.

If the above examples are not the case for you, optimizing prompts can prove to be more beneficial.
< > Update on GitHub

←Image tasks with IDEFICS
Use fast tokenizers from 🤗 Tokenizers→
LLM prompting guide
Basics of prompting
Types of models
Base vs instruct/chat models
NLP tasks
Text classification
Named Entity Recognition
Translation
Text summarization
Question answering
Reasoning
Best practices of LLM prompting
Advanced prompting techniques
Few-shot prompting
Chain-of-thought
Prompting vs fine-tuning


#### ChatGPT:
<time datetime="2025-01-07T04:24:48.967Z" title="1/7/2025, 1:24:48 PM">13:24</time>

**Summary of Hugging Face's "LLM Prompting Guide"**

Hugging Face's "LLM Prompting Guide" serves as a comprehensive resource for understanding and optimizing prompt engineering when working with Large Language Models (LLMs) using the 🤗 Transformers library. The guide covers fundamental concepts, best practices, and advanced techniques to effectively harness the power of transformer-based models for various Natural Language Processing (NLP) tasks.

---

### **1. Introduction to Large Language Models (LLMs)**

- **Definition:** LLMs like Falcon, LLaMA, and GPT-2 are pretrained transformer models designed to predict the next token in a sequence, boasting billions of parameters trained on extensive datasets.
- **Versatility:** These models can handle multiple NLP tasks out-of-the-box through natural language prompts.

### **2. Prompt Engineering**

- **Purpose:** Crafting prompts to elicit optimal responses from LLMs, a process known as prompt engineering, which involves iterative experimentation due to the flexibility and sensitivity of natural language.
- **Best Practices:** The guide outlines strategies to minimize ambiguity and maximize clarity in prompts to achieve consistent and accurate outputs.

### **3. Basics of Prompting**

- **Types of Models:**
  - **Decoder-Only Transformers:** Examples include GPT-2, LLaMA, and Falcon, primarily used for generative tasks.
  - **Encoder-Decoder Transformers:** Examples include Flan-T5 and BART, ideal for tasks where output heavily depends on the input, such as translation and summarization.
- **Pipeline Usage:**
  - **Text Generation Pipeline:** For decoder-only models.
  - **Text2Text Generation Pipeline:** For encoder-decoder models.
- **Base vs. Instruct/Chat Models:**
  - **Base Models:** Excel at text completion but lack instruction-following capabilities.
  - **Instruct/Chat Models:** Fine-tuned on instruction and conversational data, making them better suited for tasks requiring adherence to specific guidelines.

### **4. NLP Tasks and Prompt Examples**

- **Text Classification (Sentiment Analysis):**
  - **Example Prompt:** Instructs the model to classify text sentiment as positive, negative, or neutral.
- **Named Entity Recognition (NER):**
  - **Example Prompt:** Directs the model to extract and list named entities from a given text.
- **Translation:**
  - **Example Prompt:** Guides the model to translate text from one language to another.
- **Text Summarization:**
  - **Example Prompt:** Asks the model to generate a concise summary of a provided passage.
- **Question Answering:**
  - **Example Prompt:** Structures the prompt with context and a specific question to elicit accurate answers.
- **Reasoning:**
  - **Basic Prompts:** Can handle simple arithmetic but may falter with complexity.
  - **Advanced Techniques:** Incorporates Chain-of-Thought (CoT) prompting to improve reasoning by guiding the model through intermediate steps.

### **5. Best Practices for LLM Prompting**

- **Model Selection:** Opt for the latest and most capable models for better performance.
- **Prompt Design:**
  - Start simple and iterate.
  - Place instructions at the beginning or end of the prompt to leverage model attention optimally.
  - Clearly separate instructions from the input text.
  - Be specific about the desired outcome, including format, length, and style.
  - Avoid ambiguity and prefer affirmative instructions ("what to do") over negative ones ("what not to do").
  - Lead the model by initiating the response (e.g., starting the first word or sentence).
- **Testing and Iteration:**
  - Experiment with different models to ensure prompt robustness.
  - Version and track prompt performance for continuous improvement.

### **6. Advanced Prompting Techniques**

- **Few-Shot Prompting:**
  - **Definition:** Provides examples within the prompt to guide the model's responses.
  - **Usage:** Enhances performance on tasks with additional context or complexity.
  - **Limitations:** Not ideal for highly complex reasoning, can lead to lengthy prompts, and may inadvertently introduce unintended patterns.
- **Chain-of-Thought (CoT) Prompting:**
  - **Definition:** Encourages the model to articulate intermediate reasoning steps.
  - **Methods:**
    - **Few-Shot CoT:** Includes examples with detailed reasoning.
    - **Instructional CoT:** Uses phrases like "Let’s think step by step" to prompt the model.
  - **Benefit:** Improves accuracy on complex reasoning tasks by breaking down the problem-solving process.

### **7. Prompting vs. Fine-Tuning**

- **When to Fine-Tune:**
  - **Domain-Specific Needs:** When working within specialized domains not well-covered by pretraining data.
  - **Low-Resource Languages:** Enhancing model performance in languages with limited training data.
  - **Sensitive Data:** Ensuring compliance with regulations by training on secure datasets.
  - **Resource Constraints:** Situations requiring smaller models due to cost or infrastructure limitations.
- **Considerations:** Fine-tuning requires access to domain-specific datasets, computational resources, and time, making prompt optimization a preferable approach when feasible.

### **8. Additional Resources**

- **Text Generation Strategies:** Detailed exploration of parameters affecting text coherence and variability.
- **Performance Optimization:** Techniques for efficient model training and inference, including distributed training and hardware-specific optimizations.
- **Community and Contributions:** Encourages collaboration and contributions to the 🤗 Transformers ecosystem, fostering a supportive community for ongoing advancements.

---

**Conclusion**

Hugging Face's "LLM Prompting Guide" is an essential toolkit for developers and researchers aiming to leverage transformer-based models effectively. By adhering to best practices in prompt engineering and utilizing advanced techniques like few-shot and Chain-of-Thought prompting, users can significantly enhance the performance and reliability of their NLP applications. Additionally, understanding when to fine-tune models versus optimizing prompts ensures that solutions are both efficient and tailored to specific use cases.

For more detailed information and practical examples, visit the [Hugging Face Transformers documentation](https://huggingface.co/docs/transformers).


#### You:
<time datetime="2025-01-07T05:08:20.217Z" title="1/7/2025, 2:08:20 PM">14:08</time>

Using this information, describe how to write effective prompts. Create a prompt that can be used  to help me refine my questions into effective prompts

#### ChatGPT:
<time datetime="2025-01-07T05:09:34.174Z" title="1/7/2025, 2:09:34 PM">14:09</time>

Below is a concise overview of how to write effective prompts, followed by an example “meta-prompt” that guides an AI model to help you refine your questions into high-quality prompts.

---

## **How to Write Effective Prompts**

1. **Start or End with Clear Instructions**
   - Place important details and directives at the very beginning or the very end of your prompt.
   - This helps the model focus on the essentials and reduces confusion.

2. **Be Specific and Descriptive**
   - Clearly state what the model should do (e.g., “summarize,” “translate,” “classify”).
   - Mention desired details such as format, length, style, or language.

3. **Use a Clear Structure**
   - Separate different sections of the prompt with headings or signposts (e.g., “Instruction:…,” “Context:…,” “Question:…”).
   - Make it easy for the model to parse the task requirements.

4. **Provide Examples (Few-Shot Prompting)**
   - If the task is complex, give one or more examples of the question-answer format you want.
   - This nudges the model to follow patterns that lead to better results.

5. **Lead the Model**
   - Consider starting the answer for the model by providing the first word or phrase of the desired output.
   - This can reduce ambiguity and guide the model’s style or tone.

6. **Avoid Negatives**
   - Instead of telling the model what *not* to do, explicitly tell it what you *want* it to do.
   - Positive, clear instructions often yield more consistent results.

7. **Iterate and Test**
   - Refine your prompt with multiple trials; small changes in wording can produce large differences in the output.
   - Track and version your prompts if you’re working on complex projects.

---

## **Example Prompt for Refining Your Questions**

You can paste this prompt into a large language model to help you transform your rough questions into effective prompts:

```
You are an expert prompt engineering assistant. 

**Your Role**: 
- Help me refine any question or request I provide into a clear, structured, and highly effective prompt for a Large Language Model.

**Your Task**:
1. Read my initial question or request carefully.
2. Identify any ambiguities, missing details, or places where more specificity is needed.
3. Suggest improvements by:
   - Rewriting the prompt in a clearer or more detailed way.
   - Separating instructions from context.
   - Providing any examples or additional guidance the prompt might need.
4. Produce the refined prompt.

**Important**:
- Always place the most critical instructions or details at the beginning or the end.
- If needed, include bullet points or headings to clarify instructions.
- Do not change the core meaning of the original question or request; only clarify and improve it.

**Now, here is my question**:

[Insert your question here]

**End of question**.
```

**How to Use It**

1. Copy and paste the above prompt into your model interface.
2. Replace “\[Insert your question here]” with the actual question you want to refine.
3. Review the AI’s output and see how it suggests reorganizing and clarifying your question.
4. If needed, tweak the refined prompt or ask for additional improvements until it fits your exact needs.

---

**Why This Prompt Works**

- It clearly defines the AI’s role (“an expert prompt engineering assistant”).
- It uses a step-by-step outline of what to do, placed at the beginning.
- It reiterates the key constraints, such as preserving the original meaning but clarifying it.
- It provides enough instruction for the AI to systematically approach the task of prompt refinement.

By following these guidelines and using the example “meta-prompt,” you can iteratively transform any rough question into a polished, well-structured prompt that maximizes the clarity and relevance of your AI’s responses.


#### You:
<time datetime="2025-01-07T05:11:12.163Z" title="1/7/2025, 2:11:12 PM">14:11</time>

What are some possible downsides with this prompt? Could the prompt be improved to be more effective after considering these downsides?

#### ChatGPT:
<time datetime="2025-01-07T05:13:24.213Z" title="1/7/2025, 2:13:24 PM">14:13</time>

Below are several potential downsides to the “expert prompt engineering assistant” prompt, followed by suggestions on how you could refine it to address these issues and improve its effectiveness.

---

## **Potential Downsides**

1. **Overly Broad or Generic Instructions**
   - The prompt is general and may not handle domain-specific questions well. If a user’s query involves specialized topics (e.g., legal, medical, scientific), the prompt might not guide the model on how to preserve domain nuances.

2. **Lack of Response Format Guidelines**
   - The prompt does not specify whether the refined prompt should be brief or detailed, or whether it should be given in bullet points, paragraphs, or a structured markup. This can lead to unpredictably formatted answers.

3. **Ambiguity in Handling Incomplete or Contradictory Requests**
   - The prompt instructs the AI to look for ambiguities and missing details, but it doesn’t explain what to do if the user’s original question is contradictory or extremely vague.

4. **Insufficient Guidance on Tone or Style**
   - The prompt doesn’t specify whether the refined prompt should be casual, formal, technical, or optimized for a particular audience. As a result, the style of the AI’s suggestions could mismatch the user’s needs.

5. **No Mechanism for Validation or Feedback Loop**
   - There’s no instruction for the AI to confirm whether the user is satisfied with the refined prompt or to iterate further. Users may need multiple cycles to polish their prompt without a built-in “iteration request” step.

6. **Risk of Overriding the User’s Original Intent**
   - Despite stating “Do not change the core meaning,” the AI could inadvertently alter the question’s spirit or add unwarranted details. There is no explicit check to ensure minimal distortion of the original content.

7. **No Control Over Length or Complexity**
   - The prompt doesn’t set boundaries for how elaborate or concise the final refined prompt should be, which could lead to overly verbose or overly terse suggestions.

---

## **Possible Improvements**

Below is an improved version of the prompt. It incorporates additional guidelines to address the above downsides, including domain specificity, response format, iterative refinement, and style considerations.

---

### **Refined Prompt:**

```
You are an expert prompt engineering assistant with specialized knowledge of various domains (e.g., legal, medical, technical). 

**Your Role**:
- Help refine any question or request I provide into a precise, structured, and effective prompt for a Large Language Model (LLM).

**Your Task**:
1. Read my initial question or request carefully, noting any domain-specific details that might require specialized handling.
2. Identify ambiguities, missing details, or conflicting instructions within the request.
3. Suggest a clear, concise, and well-structured version of the prompt that maintains the user’s original intent. Ensure you:
   - Preserve important context and domain-specific nuances.
   - Maintain a consistent style (formal, informal, technical) based on the original request.
   - Use headings or bullet points where appropriate.
4. Provide a brief explanation of the changes or improvements you made and why.

**Important**:
- Always place the most critical instructions or details at the beginning or the end.
- Keep the final prompt reasonably concise (no more than 200 words unless necessary).
- Do not add new information beyond the scope of the original query unless absolutely needed to resolve ambiguities.
- If the user’s request is contradictory or incomplete, politely note the issue and propose how to clarify it.

**Iteration**:
- After producing your refined prompt, ask if the user is satisfied or needs further revisions.
- If needed, incorporate user feedback and refine again.

**Now, here is my question**:

[Insert your question here]

**End of question**.
```

### **Why This Version Is More Effective**

1. **Domain Awareness**: It explicitly mentions specialized domains, reminding the AI to be attentive to subject-specific terminology and context.
2. **Clear Response Format**: It outlines how the final prompt should look (headings, bullet points, concise length).
3. **Handling Incomplete or Contradictory Requests**: Provides instructions for what to do if the request is unclear, contradictory, or lacking information.
4. **Guidance on Tone and Style**: Encourages the AI to detect and maintain the style implied in the original text or domain.
5. **Built-in Iteration and Validation**: Asks the AI to confirm if more revisions are needed, creating a feedback loop.
6. **Limits on Length**: Ensures the refined prompt remains concise and prevents overly verbose outputs.
7. **Explanation of Improvements**: Instructs the AI to explain the reasons for each change, which helps the user understand the transformation process and maintain alignment with the original intent.

---

**Conclusion**\
By addressing the downsides—such as ambiguity, lack of structure, domain specificity, and iteration—this improved prompt setup ensures a more tailored, user-friendly experience. It strikes a balance between flexibility and precision, ultimately making the refined prompt more useful for both the user and the Large Language Model.
