---
title: Update LangChain Script
source: https://chatgpt.com/c/67a43dd9-603c-8003-9d19-aaffc57b7f29
---

# Update LangChain Script

#### You:
<time datetime="2025-02-06T04:44:24.524Z" title="2/6/2025, 1:44:24 PM">13:44</time>

update this script to print the result 

Skip to main content
🦜🔗 LangChain documentation - Home

    Reference

⌘
+
K
Docs

GitHub

    X / Twitter

Section Navigation

Base packages

    Core

    agents
    beta
    caches
    callbacks
    chat_history
    chat_loaders
    chat_sessions
    document_loaders
    documents
    embeddings
    example_selectors
    exceptions
    globals
    indexing
    language_models
    load
    messages
    output_parsers
    outputs
    prompt_values
    prompts

            BasePromptTemplate
            AIMessagePromptTemplate
            BaseChatPromptTemplate
            BaseMessagePromptTemplate
            BaseStringMessagePromptTemplate
            ChatMessagePromptTemplate
            ChatPromptTemplate
            HumanMessagePromptTemplate
            MessagesPlaceholder
            SystemMessagePromptTemplate
            FewShotChatMessagePromptTemplate
            FewShotPromptTemplate
            FewShotPromptWithTemplates
            ImagePromptTemplate
            PromptTemplate
            StringPromptTemplate
            StructuredPrompt
            aformat_document
            format_document
            load_prompt
            load_prompt_from_config
            check_valid_template
            get_template_variables
            jinja2_formatter
            mustache_formatter
            mustache_schema
            mustache_template_vars
            validate_jinja2
            PipelinePromptTemplate
        rate_limiters
        retrievers
        runnables
        stores
        structured_query
        sys_info
        tools
        tracers
        utils
        vectorstores
    Langchain
    Text Splitters
    Community
    Experimental

Integrations

    AI21
    Anthropic
    AstraDB
    AWS
    Azure Dynamic Sessions
    Cerebras
    Chroma
    Cohere
    Deepseek
    Elasticsearch
    Exa
    Fireworks
    Google Community
    Google GenAI
    Google VertexAI
    Groq
    Huggingface
    IBM
    Milvus
    MistralAI
    Neo4J
    Nomic
    Nvidia Ai Endpoints
    Ollama
    OpenAI
    Pinecone
    Postgres
    Prompty
    Qdrant
    Redis
    Sema4
    Snowflake
    Sqlserver
    Standard Tests
    Together
    Unstructured
    Upstage
    VoyageAI
    Weaviate
    XAI

    LangChain Python API Reference
    langchain-core: 0.3.33
    prompts
    ChatPromptTemplate

ChatPromptTemplate
class langchain_core.prompts.chat.ChatPromptTemplate
[source]

Bases: BaseChatPromptTemplate

Prompt template for chat models.

Use to create flexible templated prompts for chat models.

Examples

Changed in version 0.2.24: You can pass any Message-like formats supported by ChatPromptTemplate.from_messages() directly to ChatPromptTemplate() init.

from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate([
    ("system", "You are a helpful AI bot. Your name is {name}."),
    ("human", "Hello, how are you doing?"),
    ("ai", "I'm doing well, thanks!"),
    ("human", "{user_input}"),
])

prompt_value = template.invoke(
    {
        "name": "Bob",
        "user_input": "What is your name?"
    }
)
# Output:
# ChatPromptValue(
#    messages=[
#        SystemMessage(content='You are a helpful AI bot. Your name is Bob.'),
#        HumanMessage(content='Hello, how are you doing?'),
#        AIMessage(content="I'm doing well, thanks!"),
#        HumanMessage(content='What is your name?')
#    ]
#)

Messages Placeholder:

    # In addition to Human/AI/Tool/Function messages,
    # you can initialize the template with a MessagesPlaceholder
    # either using the class directly or with the shorthand tuple syntax:

    template = ChatPromptTemplate([
        ("system", "You are a helpful AI bot."),
        # Means the template will receive an optional list of messages under
        # the "conversation" key
        ("placeholder", "{conversation}")
        # Equivalently:
        # MessagesPlaceholder(variable_name="conversation", optional=True)
    ])

    prompt_value = template.invoke(
        {
            "conversation": [
                ("human", "Hi!"),
                ("ai", "How can I assist you today?"),
                ("human", "Can you make me an ice cream sundae?"),
                ("ai", "No.")
            ]
        }
    )

    # Output:
    # ChatPromptValue(
    #    messages=[
    #        SystemMessage(content='You are a helpful AI bot.'),
    #        HumanMessage(content='Hi!'),
    #        AIMessage(content='How can I assist you today?'),
    #        HumanMessage(content='Can you make me an ice cream sundae?'),
    #        AIMessage(content='No.'),
    #    ]
    #)

Single-variable template:

    If your prompt has only a single input variable (i.e., 1 instance of “{variable_nams}”), and you invoke the template with a non-dict object, the prompt template will inject the provided argument into that variable location.

    from langchain_core.prompts import ChatPromptTemplate

    template = ChatPromptTemplate([
        ("system", "You are a helpful AI bot. Your name is Carl."),
        ("human", "{user_input}"),
    ])

    prompt_value = template.invoke("Hello, there!")
    # Equivalent to
    # prompt_value = template.invoke({"user_input": "Hello, there!"})

    # Output:
    #  ChatPromptValue(
    #     messages=[
    #         SystemMessage(content='You are a helpful AI bot. Your name is Carl.'),
    #         HumanMessage(content='Hello, there!'),
    #     ]
    # )

Create a chat prompt template from a variety of message formats.

Parameters:

        messages – sequence of message representations. A message can be represented using the following formats: (1) BaseMessagePromptTemplate, (2) BaseMessage, (3) 2-tuple of (message type, template); e.g., (“human”, “{user_input}”), (4) 2-tuple of (message class, template), (5) a string which is shorthand for (“human”, template); e.g., “{user_input}”.

        template_format – format of the template. Defaults to “f-string”.

        input_variables – A list of the names of the variables whose values are required as inputs to the prompt.

        optional_variables – A list of the names of the variables for placeholder

        inferred (or MessagePlaceholder that are optional. These variables are auto)

        them. (from the prompt and user need not provide)

        partial_variables – A dictionary of the partial variables the prompt template carries. Partial variables populate the template so that you don’t need to pass them in every time you call the prompt.

        validate_template – Whether to validate the template.

        input_types – A dictionary of the types of the variables the prompt template expects. If not provided, all variables are assumed to be strings.

Returns:

    A chat prompt template.

Examples

Instantiation from a list of message templates:

template = ChatPromptTemplate([
    ("human", "Hello, how are you?"),
    ("ai", "I'm doing well, thanks!"),
    ("human", "That's good to hear."),
])

Instantiation from mixed message formats:

template = ChatPromptTemplate([
    SystemMessage(content="hello"),
    ("human", "Hello, how are you?"),
])

Note

ChatPromptTemplate implements the standard Runnable Interface. 🏃

The Runnable Interface has additional methods that are available on runnables, such as with_types, with_retry, assign, bind, get_graph, and more.

param input_types: Dict[str, Any] [Optional]

    A dictionary of the types of the variables the prompt template expects. If not provided, all variables are assumed to be strings.

param input_variables: list[str] [Required]

    A list of the names of the variables whose values are required as inputs to the prompt.

param messages: Annotated[list[MessageLike], SkipValidation()] [Required]

    List of messages consisting of either message prompt templates or messages.

param metadata: Dict[str, Any] | None = None

    Metadata to be used for tracing.

param optional_variables: list[str] = []

    optional_variables: A list of the names of the variables for placeholder or MessagePlaceholder that are optional. These variables are auto inferred from the prompt and user need not provide them.

param output_parser: BaseOutputParser | None = None

    How to parse the output of calling an LLM on this formatted prompt.

param partial_variables: Mapping[str, Any] [Optional]

    A dictionary of the partial variables the prompt template carries.

    Partial variables populate the template so that you don’t need to pass them in every time you call the prompt.

param tags: list[str] | None = None

    Tags to be used for tracing.

param validate_template: bool = False

    Whether or not to try validating the template.

async abatch(inputs: list[Input], config: RunnableConfig | list[RunnableConfig] | None = None, *, return_exceptions: bool = False, **kwargs: Any | None) → list[Output]

    Default implementation runs ainvoke in parallel using asyncio.gather.

    The default implementation of batch works well for IO bound runnables.

    Subclasses should override this method if they can batch more efficiently; e.g., if the underlying Runnable uses an API which supports a batch mode.

    Parameters:

            inputs (list[Input]) – A list of inputs to the Runnable.

            config (RunnableConfig | list[RunnableConfig] | None) – A config to use when invoking the Runnable. The config supports standard keys like ‘tags’, ‘metadata’ for tracing purposes, ‘max_concurrency’ for controlling how much work to do in parallel, and other keys. Please refer to the RunnableConfig for more details. Defaults to None.

            return_exceptions (bool) – Whether to return exceptions instead of raising them. Defaults to False.

            kwargs (Any | None) – Additional keyword arguments to pass to the Runnable.

    Returns:

        A list of outputs from the Runnable.
    Return type:

        list[Output]

async abatch_as_completed(inputs: Sequence[Input], config: RunnableConfig | Sequence[RunnableConfig] | None = None, *, return_exceptions: bool = False, **kwargs: Any | None) → AsyncIterator[tuple[int, Output | Exception]]

    Run ainvoke in parallel on a list of inputs, yielding results as they complete.

    Parameters:

            inputs (Sequence[Input]) – A list of inputs to the Runnable.

            config (RunnableConfig | Sequence[RunnableConfig] | None) – A config to use when invoking the Runnable. The config supports standard keys like ‘tags’, ‘metadata’ for tracing purposes, ‘max_concurrency’ for controlling how much work to do in parallel, and other keys. Please refer to the RunnableConfig for more details. Defaults to None. Defaults to None.

            return_exceptions (bool) – Whether to return exceptions instead of raising them. Defaults to False.

            kwargs (Any | None) – Additional keyword arguments to pass to the Runnable.

    Yields:

        A tuple of the index of the input and the output from the Runnable.
    Return type:

        AsyncIterator[tuple[int, Output | Exception]]

async aformat(**kwargs: Any) → str

    Async format the chat template into a string.

    Parameters:

        **kwargs (Any) – keyword arguments to use for filling in template variables in all the template messages in this chat template.
    Returns:

        formatted string.
    Return type:

        str

async aformat_messages(**kwargs: Any) → list[BaseMessage]
[source]

    Async format the chat template into a list of finalized messages.

    Parameters:

        **kwargs (Any) – keyword arguments to use for filling in template variables in all the template messages in this chat template.
    Returns:

        list of formatted messages.
    Raises:

        ValueError – If unexpected input.
    Return type:

        list[BaseMessage]

async aformat_prompt(**kwargs: Any) → PromptValue

    Async format prompt. Should return a PromptValue.

    Parameters:

        **kwargs (Any) – Keyword arguments to use for formatting.
    Returns:

        PromptValue.
    Return type:

        PromptValue

async ainvoke(input: dict, config: RunnableConfig | None = None, **kwargs: Any) → PromptValue

    Async invoke the prompt.

    Parameters:

            input (dict) – Dict, input to the prompt.

            config (RunnableConfig | None) – RunnableConfig, configuration for the prompt.

            kwargs (Any)

    Returns:

        The output of the prompt.
    Return type:

        PromptValue

append(message: BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple[str | type, str | list[dict] | list[object]] | str) → None
[source]

    Append a message to the end of the chat template.

    Parameters:

        message (BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple[str | type, str | list[dict] | list[object]] | str) – representation of a message to append.
    Return type:

        None

async astream(input: Input, config: RunnableConfig | None = None, **kwargs: Any | None) → AsyncIterator[Output]

    Default implementation of astream, which calls ainvoke. Subclasses should override this method if they support streaming output.

    Parameters:

            input (Input) – The input to the Runnable.

            config (RunnableConfig | None) – The config to use for the Runnable. Defaults to None.

            kwargs (Any | None) – Additional keyword arguments to pass to the Runnable.

    Yields:

        The output of the Runnable.
    Return type:

        AsyncIterator[Output]

async astream_events(input: Any, config: RunnableConfig | None = None, *, version: Literal['v1', 'v2'], include_names: Sequence[str] | None = None, include_types: Sequence[str] | None = None, include_tags: Sequence[str] | None = None, exclude_names: Sequence[str] | None = None, exclude_types: Sequence[str] | None = None, exclude_tags: Sequence[str] | None = None, **kwargs: Any) → AsyncIterator[StandardStreamEvent | CustomStreamEvent]

Generate a stream of events.

Use to create an iterator over StreamEvents that provide real-time information about the progress of the Runnable, including StreamEvents from intermediate results.

A StreamEvent is a dictionary with the following schema:

    event: str - Event names are of the

        format: on_[runnable_type]_(start|stream|end).

    name: str - The name of the Runnable that generated the event.

    run_id: str - randomly generated ID associated with the given execution of

        the Runnable that emitted the event. A child Runnable that gets invoked as part of the execution of a parent Runnable is assigned its own unique ID.

    parent_ids: List[str] - The IDs of the parent runnables that

        generated the event. The root Runnable will have an empty list. The order of the parent IDs is from the root to the immediate parent. Only available for v2 version of the API. The v1 version of the API will return an empty list.

    tags: Optional[List[str]] - The tags of the Runnable that generated

        the event.

    metadata: Optional[Dict[str, Any]] - The metadata of the Runnable

        that generated the event.

    data: Dict[str, Any]

Below is a table that illustrates some events that might be emitted by various chains. Metadata fields have been omitted from the table for brevity. Chain definitions have been included after the table.

ATTENTION This reference table is for the V2 version of the schema.

event
	

name
	

chunk
	

input
	

output

on_chat_model_start
	

[model name]
		

{“messages”: [[SystemMessage, HumanMessage]]}
	

on_chat_model_stream
	

[model name]
	

AIMessageChunk(content=”hello”)
		

on_chat_model_end
	

[model name]
		

{“messages”: [[SystemMessage, HumanMessage]]}
	

AIMessageChunk(content=”hello world”)

on_llm_start
	

[model name]
		

{‘input’: ‘hello’}
	

on_llm_stream
	

[model name]
	

‘Hello’
		

on_llm_end
	

[model name]
		

‘Hello human!’
	

on_chain_start
	

format_docs
			

on_chain_stream
	

format_docs
	

“hello world!, goodbye world!”
		

on_chain_end
	

format_docs
		

[Document(…)]
	

“hello world!, goodbye world!”

on_tool_start
	

some_tool
		

{“x”: 1, “y”: “2”}
	

on_tool_end
	

some_tool
			

{“x”: 1, “y”: “2”}

on_retriever_start
	

[retriever name]
		

{“query”: “hello”}
	

on_retriever_end
	

[retriever name]
		

{“query”: “hello”}
	

[Document(…), ..]

on_prompt_start
	

[template_name]
		

{“question”: “hello”}
	

on_prompt_end
	

[template_name]
		

{“question”: “hello”}
	

ChatPromptValue(messages: [SystemMessage, …])

In addition to the standard events, users can also dispatch custom events (see example below).

Custom events will be only be surfaced with in the v2 version of the API!

A custom event has following format:

Attribute
	

Type
	

Description

name
	

str
	

A user defined name for the event.

data
	

Any
	

The data associated with the event. This can be anything, though we suggest making it JSON serializable.

Here are declarations associated with the standard events shown above:

format_docs:

def format_docs(docs: List[Document]) -> str:
    '''Format the docs.'''
    return ", ".join([doc.page_content for doc in docs])

format_docs = RunnableLambda(format_docs)

some_tool:

@tool
def some_tool(x: int, y: str) -> dict:
    '''Some_tool.'''
    return {"x": x, "y": y}

prompt:

template = ChatPromptTemplate.from_messages(
    [("system", "You are Cat Agent 007"), ("human", "{question}")]
).with_config({"run_name": "my_template", "tags": ["my_template"]})

Example:

from langchain_core.runnables import RunnableLambda

async def reverse(s: str) -> str:
    return s[::-1]

chain = RunnableLambda(func=reverse)

events = [
    event async for event in chain.astream_events("hello", version="v2")
]

# will produce the following events (run_id, and parent_ids
# has been omitted for brevity):
[
    {
        "data": {"input": "hello"},
        "event": "on_chain_start",
        "metadata": {},
        "name": "reverse",
        "tags": [],
    },
    {
        "data": {"chunk": "olleh"},
        "event": "on_chain_stream",
        "metadata": {},
        "name": "reverse",
        "tags": [],
    },
    {
        "data": {"output": "olleh"},
        "event": "on_chain_end",
        "metadata": {},
        "name": "reverse",
        "tags": [],
    },
]

Example: Dispatch Custom Event

from langchain_core.callbacks.manager import (
    adispatch_custom_event,
)
from langchain_core.runnables import RunnableLambda, RunnableConfig
import asyncio


async def slow_thing(some_input: str, config: RunnableConfig) -> str:
    """Do something that takes a long time."""
    await asyncio.sleep(1) # Placeholder for some slow operation
    await adispatch_custom_event(
        "progress_event",
        {"message": "Finished step 1 of 3"},
        config=config # Must be included for python < 3.10
    )
    await asyncio.sleep(1) # Placeholder for some slow operation
    await adispatch_custom_event(
        "progress_event",
        {"message": "Finished step 2 of 3"},
        config=config # Must be included for python < 3.10
    )
    await asyncio.sleep(1) # Placeholder for some slow operation
    return "Done"

slow_thing = RunnableLambda(slow_thing)

async for event in slow_thing.astream_events("some_input", version="v2"):
    print(event)

    Parameters:

            input (Any) – The input to the Runnable.

            config (RunnableConfig | None) – The config to use for the Runnable.

            version (Literal['v1', 'v2']) – The version of the schema to use either v2 or v1. Users should use v2. v1 is for backwards compatibility and will be deprecated in 0.4.0. No default will be assigned until the API is stabilized. custom events will only be surfaced in v2.

            include_names (Sequence[str] | None) – Only include events from runnables with matching names.

            include_types (Sequence[str] | None) – Only include events from runnables with matching types.

            include_tags (Sequence[str] | None) – Only include events from runnables with matching tags.

            exclude_names (Sequence[str] | None) – Exclude events from runnables with matching names.

            exclude_types (Sequence[str] | None) – Exclude events from runnables with matching types.

            exclude_tags (Sequence[str] | None) – Exclude events from runnables with matching tags.

            kwargs (Any) – Additional keyword arguments to pass to the Runnable. These will be passed to astream_log as this implementation of astream_events is built on top of astream_log.

    Yields:

        An async stream of StreamEvents.
    Raises:

        NotImplementedError – If the version is not v1 or v2.
    Return type:

        AsyncIterator[StandardStreamEvent | CustomStreamEvent]

batch(inputs: list[Input], config: RunnableConfig | list[RunnableConfig] | None = None, *, return_exceptions: bool = False, **kwargs: Any | None) → list[Output]

    Default implementation runs invoke in parallel using a thread pool executor.

    The default implementation of batch works well for IO bound runnables.

    Subclasses should override this method if they can batch more efficiently; e.g., if the underlying Runnable uses an API which supports a batch mode.

    Parameters:

            inputs (list[Input])

            config (RunnableConfig | list[RunnableConfig] | None)

            return_exceptions (bool)

            kwargs (Any | None)

    Return type:

        list[Output]

batch_as_completed(inputs: Sequence[Input], config: RunnableConfig | Sequence[RunnableConfig] | None = None, *, return_exceptions: bool = False, **kwargs: Any | None) → Iterator[tuple[int, Output | Exception]]

    Run invoke in parallel on a list of inputs, yielding results as they complete.

    Parameters:

            inputs (Sequence[Input])

            config (RunnableConfig | Sequence[RunnableConfig] | None)

            return_exceptions (bool)

            kwargs (Any | None)

    Return type:

        Iterator[tuple[int, Output | Exception]]

bind(**kwargs: Any) → Runnable[Input, Output]

Bind arguments to a Runnable, returning a new Runnable.

Useful when a Runnable in a chain requires an argument that is not in the output of the previous Runnable or included in the user input.

Parameters:

    kwargs (Any) – The arguments to bind to the Runnable.
Returns:

    A new Runnable with the arguments bound.
Return type:

    Runnable[Input, Output]

Example:

from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(model='llama2')

# Without bind.
chain = (
    llm
    | StrOutputParser()
)

chain.invoke("Repeat quoted words exactly: 'One two three four five.'")
# Output is 'One two three four five.'

# With bind.
chain = (
    llm.bind(stop=["three"])
    | StrOutputParser()
)

chain.invoke("Repeat quoted words exactly: 'One two three four five.'")
# Output is 'One two'

configurable_alternatives(which: ConfigurableField, *, default_key: str = 'default', prefix_keys: bool = False, **kwargs: Runnable[Input, Output] | Callable[[], Runnable[Input, Output]]) → RunnableSerializable

Configure alternatives for Runnables that can be set at runtime.

Parameters:

        which (ConfigurableField) – The ConfigurableField instance that will be used to select the alternative.

        default_key (str) – The default key to use if no alternative is selected. Defaults to “default”.

        prefix_keys (bool) – Whether to prefix the keys with the ConfigurableField id. Defaults to False.

        **kwargs (Runnable[Input, Output] | Callable[[], Runnable[Input, Output]]) – A dictionary of keys to Runnable instances or callables that return Runnable instances.

Returns:

    A new Runnable with the alternatives configured.
Return type:

    RunnableSerializable

from langchain_anthropic import ChatAnthropic
from langchain_core.runnables.utils import ConfigurableField
from langchain_openai import ChatOpenAI

model = ChatAnthropic(
    model_name="claude-3-sonnet-20240229"
).configurable_alternatives(
    ConfigurableField(id="llm"),
    default_key="anthropic",
    openai=ChatOpenAI()
)

# uses the default model ChatAnthropic
print(model.invoke("which organization created you?").content)

# uses ChatOpenAI
print(
    model.with_config(
        configurable={"llm": "openai"}
    ).invoke("which organization created you?").content
)

configurable_fields(**kwargs: ConfigurableField | ConfigurableFieldSingleOption | ConfigurableFieldMultiOption) → RunnableSerializable

Configure particular Runnable fields at runtime.

Parameters:

    **kwargs (ConfigurableField | ConfigurableFieldSingleOption | ConfigurableFieldMultiOption) – A dictionary of ConfigurableField instances to configure.
Returns:

    A new Runnable with the fields configured.
Return type:

    RunnableSerializable

from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

model = ChatOpenAI(max_tokens=20).configurable_fields(
    max_tokens=ConfigurableField(
        id="output_token_number",
        name="Max tokens in the output",
        description="The maximum number of tokens in the output",
    )
)

# max_tokens = 20
print(
    "max_tokens_20: ",
    model.invoke("tell me something about chess").content
)

# max_tokens = 200
print("max_tokens_200: ", model.with_config(
    configurable={"output_token_number": 200}
    ).invoke("tell me something about chess").content
)

extend(messages: Sequence[BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple[str | type, str | list[dict] | list[object]] | str]) → None
[source]

    Extend the chat template with a sequence of messages.

    Parameters:

        messages (Sequence[BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple[str | type, str | list[dict] | list[object]] | str]) – sequence of message representations to append.
    Return type:

        None

format(**kwargs: Any) → str

    Format the chat template into a string.

    Parameters:

        **kwargs (Any) – keyword arguments to use for filling in template variables in all the template messages in this chat template.
    Returns:

        formatted string.
    Return type:

        str

format_messages(**kwargs: Any) → list[BaseMessage]
[source]

    Format the chat template into a list of finalized messages.

    Parameters:

        **kwargs (Any) – keyword arguments to use for filling in template variables in all the template messages in this chat template.
    Returns:

        list of formatted messages.
    Return type:

        list[BaseMessage]

format_prompt(**kwargs: Any) → PromptValue

    Format prompt. Should return a PromptValue.

    Parameters:

        **kwargs (Any) – Keyword arguments to use for formatting.
    Returns:

        PromptValue.
    Return type:

        PromptValue

classmethod from_messages(messages: Sequence[BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple[str | type, str | list[dict] | list[object]] | str], template_format: Literal['f-string', 'mustache', 'jinja2'] = 'f-string') → ChatPromptTemplate
[source]

Create a chat prompt template from a variety of message formats.

Examples

Instantiation from a list of message templates:

template = ChatPromptTemplate.from_messages([
    ("human", "Hello, how are you?"),
    ("ai", "I'm doing well, thanks!"),
    ("human", "That's good to hear."),
])

Instantiation from mixed message formats:

template = ChatPromptTemplate.from_messages([
    SystemMessage(content="hello"),
    ("human", "Hello, how are you?"),
])

    Parameters:

            messages (Sequence[BaseMessagePromptTemplate | BaseMessage | BaseChatPromptTemplate | tuple[str | type, str | list[dict] | list[object]] | str]) – sequence of message representations. A message can be represented using the following formats: (1) BaseMessagePromptTemplate, (2) BaseMessage, (3) 2-tuple of (message type, template); e.g., (“human”, “{user_input}”), (4) 2-tuple of (message class, template), (5) a string which is shorthand for (“human”, template); e.g., “{user_input}”.

            template_format (Literal['f-string', 'mustache', 'jinja2']) – format of the template. Defaults to “f-string”.

    Returns:

        a chat prompt template.
    Return type:

        ChatPromptTemplate

classmethod from_role_strings(string_messages: list[tuple[str, str]]) → ChatPromptTemplate
[source]

    Deprecated since version 0.0.1: Use from_messages classmethod() instead.

    Create a chat prompt template from a list of (role, template) tuples.

    Parameters:

        string_messages (list[tuple[str, str]]) – list of (role, template) tuples.
    Returns:

        a chat prompt template.
    Return type:

        ChatPromptTemplate

classmethod from_strings(string_messages: list[tuple[type[BaseMessagePromptTemplate], str]]) → ChatPromptTemplate
[source]

    Deprecated since version 0.0.1: Use from_messages classmethod() instead.

    Create a chat prompt template from a list of (role class, template) tuples.

    Parameters:

        string_messages (list[tuple[type[BaseMessagePromptTemplate], str]]) – list of (role class, template) tuples.
    Returns:

        a chat prompt template.
    Return type:

        ChatPromptTemplate

classmethod from_template(template: str, **kwargs: Any) → ChatPromptTemplate
[source]

    Create a chat prompt template from a template string.

    Creates a chat template consisting of a single message assumed to be from the human.

    Parameters:

            template (str) – template string

            **kwargs (Any) – keyword arguments to pass to the constructor.

    Returns:

        A new instance of this class.
    Return type:

        ChatPromptTemplate

invoke(input: dict, config: RunnableConfig | None = None, **kwargs: Any) → PromptValue

    Invoke the prompt.

    Parameters:

            input (dict) – Dict, input to the prompt.

            config (RunnableConfig | None) – RunnableConfig, configuration for the prompt.

            kwargs (Any)

    Returns:

        The output of the prompt.
    Return type:

        PromptValue

partial(**kwargs: Any) → ChatPromptTemplate
[source]

Get a new ChatPromptTemplate with some input variables already filled in.

Parameters:

    **kwargs (Any) – keyword arguments to use for filling in template variables. Ought to be a subset of the input variables.
Returns:

    A new ChatPromptTemplate.
Return type:

    ChatPromptTemplate

Example

from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI assistant named {name}."),
        ("human", "Hi I'm {user}"),
        ("ai", "Hi there, {user}, I'm {name}."),
        ("human", "{input}"),
    ]
)
template2 = template.partial(user="Lucy", name="R2D2")

template2.format_messages(input="hello")

pretty_print() → None

    Print a human-readable representation.

    Return type:

        None

pretty_repr(html: bool = False) → str
[source]

    Human-readable representation.

    Parameters:

        html (bool) – Whether to format as HTML. Defaults to False.
    Returns:

        Human-readable representation.
    Return type:

        str

save(file_path: Path | str) → None
[source]

    Save prompt to file.

    Parameters:

        file_path (Path | str) – path to file.
    Return type:

        None

stream(input: Input, config: RunnableConfig | None = None, **kwargs: Any | None) → Iterator[Output]

    Default implementation of stream, which calls invoke. Subclasses should override this method if they support streaming output.

    Parameters:

            input (Input) – The input to the Runnable.

            config (RunnableConfig | None) – The config to use for the Runnable. Defaults to None.

            kwargs (Any | None) – Additional keyword arguments to pass to the Runnable.

    Yields:

        The output of the Runnable.
    Return type:

        Iterator[Output]

with_alisteners(*, on_start: AsyncListener | None = None, on_end: AsyncListener | None = None, on_error: AsyncListener | None = None) → Runnable[Input, Output]

Bind async lifecycle listeners to a Runnable, returning a new Runnable.

on_start: Asynchronously called before the Runnable starts running. on_end: Asynchronously called after the Runnable finishes running. on_error: Asynchronously called if the Runnable throws an error.

The Run object contains information about the run, including its id, type, input, output, error, start_time, end_time, and any tags or metadata added to the run.

Parameters:

        on_start (Optional[AsyncListener]) – Asynchronously called before the Runnable starts running. Defaults to None.

        on_end (Optional[AsyncListener]) – Asynchronously called after the Runnable finishes running. Defaults to None.

        on_error (Optional[AsyncListener]) – Asynchronously called if the Runnable throws an error. Defaults to None.

Returns:

    A new Runnable with the listeners bound.
Return type:

    Runnable[Input, Output]

Example:

from langchain_core.runnables import RunnableLambda
import time

async def test_runnable(time_to_sleep : int):
    print(f"Runnable[{time_to_sleep}s]: starts at {format_t(time.time())}")
    await asyncio.sleep(time_to_sleep)
    print(f"Runnable[{time_to_sleep}s]: ends at {format_t(time.time())}")

async def fn_start(run_obj : Runnable):
    print(f"on start callback starts at {format_t(time.time())}
    await asyncio.sleep(3)
    print(f"on start callback ends at {format_t(time.time())}")

async def fn_end(run_obj : Runnable):
    print(f"on end callback starts at {format_t(time.time())}
    await asyncio.sleep(2)
    print(f"on end callback ends at {format_t(time.time())}")

runnable = RunnableLambda(test_runnable).with_alisteners(
    on_start=fn_start,
    on_end=fn_end
)
async def concurrent_runs():
    await asyncio.gather(runnable.ainvoke(2), runnable.ainvoke(3))

asyncio.run(concurrent_runs())
Result:
on start callback starts at 2024-05-16T14:20:29.637053+00:00
on start callback starts at 2024-05-16T14:20:29.637150+00:00
on start callback ends at 2024-05-16T14:20:32.638305+00:00
on start callback ends at 2024-05-16T14:20:32.638383+00:00
Runnable[3s]: starts at 2024-05-16T14:20:32.638849+00:00
Runnable[5s]: starts at 2024-05-16T14:20:32.638999+00:00
Runnable[3s]: ends at 2024-05-16T14:20:35.640016+00:00
on end callback starts at 2024-05-16T14:20:35.640534+00:00
Runnable[5s]: ends at 2024-05-16T14:20:37.640169+00:00
on end callback starts at 2024-05-16T14:20:37.640574+00:00
on end callback ends at 2024-05-16T14:20:37.640654+00:00
on end callback ends at 2024-05-16T14:20:39.641751+00:00

with_config(config: RunnableConfig | None = None, **kwargs: Any) → Runnable[Input, Output]

    Bind config to a Runnable, returning a new Runnable.

    Parameters:

            config (RunnableConfig | None) – The config to bind to the Runnable.

            kwargs (Any) – Additional keyword arguments to pass to the Runnable.

    Returns:

        A new Runnable with the config bound.
    Return type:

        Runnable[Input, Output]

with_fallbacks(fallbacks: Sequence[Runnable[Input, Output]], *, exceptions_to_handle: tuple[type[BaseException], ...] = (<class 'Exception'>,), exception_key: Optional[str] = None) → RunnableWithFallbacksT[Input, Output]

Add fallbacks to a Runnable, returning a new Runnable.

The new Runnable will try the original Runnable, and then each fallback in order, upon failures.

Parameters:

        fallbacks (Sequence[Runnable[Input, Output]]) – A sequence of runnables to try if the original Runnable fails.

        exceptions_to_handle (tuple[type[BaseException], ...]) – A tuple of exception types to handle. Defaults to (Exception,).

        exception_key (Optional[str]) – If string is specified then handled exceptions will be passed to fallbacks as part of the input under the specified key. If None, exceptions will not be passed to fallbacks. If used, the base Runnable and its fallbacks must accept a dictionary as input. Defaults to None.

Returns:

    A new Runnable that will try the original Runnable, and then each fallback in order, upon failures.
Return type:

    RunnableWithFallbacksT[Input, Output]

Example

from typing import Iterator

from langchain_core.runnables import RunnableGenerator


def _generate_immediate_error(input: Iterator) -> Iterator[str]:
    raise ValueError()
    yield ""


def _generate(input: Iterator) -> Iterator[str]:
    yield from "foo bar"


runnable = RunnableGenerator(_generate_immediate_error).with_fallbacks(
    [RunnableGenerator(_generate)]
    )
print(''.join(runnable.stream({}))) #foo bar

    Parameters:

            fallbacks (Sequence[Runnable[Input, Output]]) – A sequence of runnables to try if the original Runnable fails.

            exceptions_to_handle (tuple[type[BaseException], ...]) – A tuple of exception types to handle.

            exception_key (Optional[str]) – If string is specified then handled exceptions will be passed to fallbacks as part of the input under the specified key. If None, exceptions will not be passed to fallbacks. If used, the base Runnable and its fallbacks must accept a dictionary as input.

    Returns:

        A new Runnable that will try the original Runnable, and then each fallback in order, upon failures.
    Return type:

        RunnableWithFallbacksT[Input, Output]

with_listeners(*, on_start: Callable[[Run], None] | Callable[[Run, RunnableConfig], None] | None = None, on_end: Callable[[Run], None] | Callable[[Run, RunnableConfig], None] | None = None, on_error: Callable[[Run], None] | Callable[[Run, RunnableConfig], None] | None = None) → Runnable[Input, Output]

Bind lifecycle listeners to a Runnable, returning a new Runnable.

on_start: Called before the Runnable starts running, with the Run object. on_end: Called after the Runnable finishes running, with the Run object. on_error: Called if the Runnable throws an error, with the Run object.

The Run object contains information about the run, including its id, type, input, output, error, start_time, end_time, and any tags or metadata added to the run.

Parameters:

        on_start (Optional[Union[Callable[[Run], None], Callable[[Run, RunnableConfig], None]]]) – Called before the Runnable starts running. Defaults to None.

        on_end (Optional[Union[Callable[[Run], None], Callable[[Run, RunnableConfig], None]]]) – Called after the Runnable finishes running. Defaults to None.

        on_error (Optional[Union[Callable[[Run], None], Callable[[Run, RunnableConfig], None]]]) – Called if the Runnable throws an error. Defaults to None.

Returns:

    A new Runnable with the listeners bound.
Return type:

    Runnable[Input, Output]

Example:

from langchain_core.runnables import RunnableLambda
from langchain_core.tracers.schemas import Run

import time

def test_runnable(time_to_sleep : int):
    time.sleep(time_to_sleep)

def fn_start(run_obj: Run):
    print("start_time:", run_obj.start_time)

def fn_end(run_obj: Run):
    print("end_time:", run_obj.end_time)

chain = RunnableLambda(test_runnable).with_listeners(
    on_start=fn_start,
    on_end=fn_end
)
chain.invoke(2)

with_retry(*, retry_if_exception_type: tuple[type[BaseException], ...] = (<class 'Exception'>,), wait_exponential_jitter: bool = True, stop_after_attempt: int = 3) → Runnable[Input, Output]

Create a new Runnable that retries the original Runnable on exceptions.

Parameters:

        retry_if_exception_type (tuple[type[BaseException], ...]) – A tuple of exception types to retry on. Defaults to (Exception,).

        wait_exponential_jitter (bool) – Whether to add jitter to the wait time between retries. Defaults to True.

        stop_after_attempt (int) – The maximum number of attempts to make before giving up. Defaults to 3.

Returns:

    A new Runnable that retries the original Runnable on exceptions.
Return type:

    Runnable[Input, Output]

Example:

from langchain_core.runnables import RunnableLambda

count = 0


def _lambda(x: int) -> None:
    global count
    count = count + 1
    if x == 1:
        raise ValueError("x is 1")
    else:
         pass


runnable = RunnableLambda(_lambda)
try:
    runnable.with_retry(
        stop_after_attempt=2,
        retry_if_exception_type=(ValueError,),
    ).invoke(1)
except ValueError:
    pass

assert (count == 2)

    Parameters:

            retry_if_exception_type (tuple[type[BaseException], ...]) – A tuple of exception types to retry on

            wait_exponential_jitter (bool) – Whether to add jitter to the wait time between retries

            stop_after_attempt (int) – The maximum number of attempts to make before giving up

    Returns:

        A new Runnable that retries the original Runnable on exceptions.
    Return type:

        Runnable[Input, Output]

with_types(*, input_type: type[Input] | None = None, output_type: type[Output] | None = None) → Runnable[Input, Output]

        Bind input and output types to a Runnable, returning a new Runnable.

        Parameters:

                input_type (type[Input] | None) – The input type to bind to the Runnable. Defaults to None.

                output_type (type[Output] | None) – The output type to bind to the Runnable. Defaults to None.

        Returns:

            A new Runnable with the types bound.
        Return type:

            Runnable[Input, Output]

Examples using ChatPromptTemplate

    # Basic example (short documents)

    # Example

    # Legacy

    AWS DynamoDB

    Activeloop Deep Memory

    Apache Cassandra

    ApertureDB

    ArxivRetriever

    AskNews

    AzureAISearchRetriever

    AzureChatOpenAI

    Build a Chatbot

    Build a Local RAG Application

    Build a PDF ingestion and Question/Answering system

    Build a Query Analysis System

    Build a Retrieval Augmented Generation (RAG) App

    Build a Simple LLM Application with LCEL

    Build an Extraction Chain

    ChatAI21

    ChatAnthropic

    ChatBedrock

    ChatDatabricks

    ChatFireworks

    ChatGoogleGenerativeAI

    ChatGroq

    ChatMistralAI

    ChatNVIDIA

    ChatOCIGenAI

    ChatOllama

    ChatOpenAI

    ChatPerplexity

    ChatTogether

    ChatUpstage

    ChatVertexAI

    ChatWatsonx

    ChatYI

    Classify Text into Labels

    Cohere

    Conceptual guide

    Context

    Conversational RAG

    Couchbase

    Databricks Unity Catalog (UC)

    Eden AI

    ElasticsearchRetriever

    Facebook Messenger

    Fiddler

    Figma

    FinancialDatasets Toolkit

    Fleet AI Context

    Google AlloyDB for PostgreSQL

    Google El Carro Oracle

    Google SQL for MySQL

    Google SQL for PostgreSQL

    Google SQL for SQL Server

    Google Vertex AI Search

    How deal with high cardinality categoricals when doing query analysis

    How to add a semantic layer over graph database

    How to add ad-hoc tool calling capability to LLMs and Chat Models

    How to add chat history

    How to add default invocation args to a Runnable

    How to add examples to the prompt for query analysis

    How to add fallbacks to a runnable

    How to add memory to chatbots

    How to add message history

    How to add retrieval to chatbots

    How to add tools to chatbots

    How to add values to a chain’s state

    How to attach callbacks to a runnable

    How to chain runnables

    How to convert Runnables as Tools

    How to create a custom LLM class

    How to create a dynamic (self-constructing) chain

    How to create custom callback handlers

    How to create tools

    How to deal with large databases when doing SQL question-answering

    How to debug your LLM apps

    How to do per-user retrieval

    How to do query validation as part of SQL question-answering

    How to do question answering over CSVs

    How to do tool/function calling

    How to get a RAG application to add citations

    How to get your RAG application to return sources

    How to handle cases where no queries are generated

    How to handle long text when doing extraction

    How to handle multiple queries when doing query analysis

    How to handle multiple retrievers when doing query analysis

    How to handle tool errors

    How to inspect runnables

    How to invoke runnables in parallel

    How to map values to a graph database

    How to migrate from legacy LangChain agents to LangGraph

    How to pass callbacks in at runtime

    How to pass through arguments from one step to the next

    How to propagate callbacks constructor

    How to retrieve using multiple vectors per document

    How to return structured data from a model

    How to run custom functions

    How to save and load LangChain objects

    How to stream events from a tool

    How to stream results from your RAG application

    How to stream runnables

    How to summarize text in a single LLM call

    How to summarize text through iterative refinement

    How to summarize text through parallelization

    How to track token usage in ChatModels

    How to use few shot examples in chat models

    How to use few-shot prompting with tool calling

    How to use multimodal prompts

    How to use prompting alone (no tool calling) to do extraction

    How to use reference examples when doing extraction

    Hybrid Search

    Image captions

    Jaguar Vector Database

    JinaChat

    Kinetica Language To SQL Chat Model

    LangChain Expression Language Cheatsheet

    LangSmith LLM Runs

    Llama.cpp

    Llama2Chat

    Load docs

    MLflow

    Maritalk

    MongoDB

    NVIDIA NIMs

    OllamaFunctions

    OllamaLLM

    OpenAI metadata tagger

    RAGatouille

    Redis

    Riza Code Interpreter

    SQL (SQLAlchemy)

    SQLite

    Streamlit

    Summarize Text

    Tavily Search

    TavilySearchAPIRetriever

    TiDB

    UpTrain

    Vector stores and retrievers

    Weaviate

    WikipediaRetriever

    Yellowbrick

    You.com

    Yuan2.0

    ZepCloudChatMessageHistory

    iMessage

    vLLM Chat

    🦜️🏓 LangServe

On this page

    ChatPromptTemplate
        input_types
        input_variables
        messages
        metadata
        optional_variables
        output_parser
        partial_variables
        tags
        validate_template
        abatch()
        abatch_as_completed()
        aformat()
        aformat_messages()
        aformat_prompt()
        ainvoke()
        append()
        astream()
        astream_events()
        batch()
        batch_as_completed()
        bind()
        configurable_alternatives()
        configurable_fields()
        extend()
        format()
        format_messages()
        format_prompt()
        from_messages()
        from_role_strings()
        from_strings()
        from_template()
        invoke()
        partial()
        pretty_print()
        pretty_repr()
        save()
        stream()
        with_alisteners()
        with_config()
        with_fallbacks()
        with_listeners()
        with_retry()
        with_types()

© Copyright 2023, LangChain Inc.


#### ChatGPT:
<time datetime="2025-02-06T04:44:30.331Z" title="2/6/2025, 1:44:30 PM">13:44</time>

Below is the updated script that prints the resulting prompt value:

```python
from langchain_core.prompts import ChatPromptTemplate

# Define the chat prompt template with message templates
template = ChatPromptTemplate([
    ("system", "You are a helpful AI bot. Your name is {name}."),
    ("human", "Hello, how are you doing?"),
    ("ai", "I'm doing well, thanks!"),
    ("human", "{user_input}"),
])

# Invoke the template with the required variables
prompt_value = template.invoke({
    "name": "Bob",
    "user_input": "What is your name?"
})

# Print the result
print(prompt_value)
```

When you run this script, it will output a `ChatPromptValue` object containing the formatted messages:

```
ChatPromptValue(
   messages=[
       SystemMessage(content='You are a helpful AI bot. Your name is Bob.'),
       HumanMessage(content='Hello, how are you doing?'),
       AIMessage(content="I'm doing well, thanks!"),
       HumanMessage(content='What is your name?')
   ]
)
```

This shows that the template has been successfully filled in with the provided values and the result is printed to the console.
