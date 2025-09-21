---
title: Orchestrating Python Scripts
source: https://chatgpt.com/c/67800b19-dcb4-8003-876c-fe400bb5c1b8
---

# Orchestrating Python Scripts

#### You:
<time datetime="2025-01-09T17:44:58.096Z" title="1/10/2025, 2:44:58 AM">02:44</time>

I need help learning about how to orchestrate scripts. I have a buncof python scripts to accomplish various tasks, like uploading logs, editing those logs logs, and accomplishing various things in my homelab. But they only run when I execute them manually. How can I turn this folder of scripts into a system that runs all the time in the background

#### ChatGPT:
<time datetime="2025-01-09T17:46:54.352Z" title="1/10/2025, 2:46:54 AM">02:46</time>

There are several ways to run multiple Python scripts (or “jobs”) in the background so you don’t have to trigger them manually every time. Below are a few approaches, ordered roughly from simplest (e.g., cron jobs) to more complex and powerful (e.g., Airflow, systemd services, container orchestrators). Which route to choose depends on how sophisticated your setup needs to be.

---

## 1. Use Cron Jobs (or Scheduled Tasks on Windows)

### How It Works

- **cron** (on Linux/macOS) is the classic scheduler that runs commands at specified times.
- **Scheduled Tasks** on Windows is a similar built-in scheduler.

### Pros

- Very simple to set up.
- Good if your scripts need to run at regular intervals (e.g., every 10 minutes, once a day, etc.).

### Cons

- Not great for complex dependencies or workflows (e.g., if script B depends on the successful run of script A).
- Limited visibility into logs without additional configuration.

### Example: Setting up cron on Linux

1. Open your crontab:
   ```bash
   crontab -e
   ```
2. Add an entry to run a Python script every day at 5:00 AM:
   ```bash
   0 5 * * * /usr/bin/python3 /path/to/script.py >> /path/to/logfile.log 2>&1
   ```
3. Save and exit. `cron` will now trigger it automatically.

---

## 2. Use a Python Scheduler Library (e.g., APScheduler)

### How It Works

- You create a “main” Python process that runs continuously and uses APScheduler (or a similar library) to schedule your jobs.
- The scheduler can run tasks based on CRON expressions, intervals, or specific dates.

### Pros

- Pure Python solution—no external system needed beyond Python.
- More flexible than cron for orchestrating jobs, handling tasks in code, adding logic, error handling, etc.

### Cons

- You still need a way to keep this scheduler script itself running all the time (e.g., as a service or via something like `screen`, `tmux`, or Docker).

### Example: Using APScheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler
import time

def job1():
    print("Running job1...")

def job2():
    print("Running job2...")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(job1, 'interval', minutes=5)  # run every 5 minutes
    scheduler.add_job(job2, 'cron', hour=1)        # run at 1 AM every day

    scheduler.start()
    try:
        # Keep the main thread alive so the scheduler keeps running
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
```

---

## 3. Run Scripts as a System Service (systemd on Linux)

### How It Works

- Create a systemd unit file that describes your service (i.e., your Python orchestrator or a single script).
- systemd will keep the process alive and can restart it if it fails.

### Pros

- Automatically restarts on reboot or after crashes.
- Standard approach for Linux servers; logs are managed in `journalctl`.

### Cons

- Only available on systemd-based distros (which is most modern Linux distributions, but not all).
- Might be more configuration than you need for a small system.

### Example: systemd Service

1. Create a service file `/etc/systemd/system/my-orchestrator.service`:
   ```ini
   [Unit]
   Description=Python Orchestrator Service
   After=network.target

   [Service]
   Type=simple
   ExecStart=/usr/bin/python3 /home/username/scripts/orchestrator.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
2. Enable and start the service:
   ```bash
   sudo systemctl enable my-orchestrator.service
   sudo systemctl start my-orchestrator.service
   ```
3. Check status and logs:
   ```bash
   sudo systemctl status my-orchestrator.service
   journalctl -u my-orchestrator.service
   ```

---

## 4. Use a Workflow Orchestrator (e.g., Apache Airflow, Luigi, Prefect)

### How It Works

- Install a workflow orchestration platform like Airflow, Luigi, or Prefect.
- Define Directed Acyclic Graphs (DAGs) or flows describing which script depends on which others, how often to run, etc.
- A web UI usually shows you the job status and logs.

### Pros

- Designed for complex workflows with dependencies.
- Built-in scheduling, logging, monitoring, error handling, and retries.
- Great if you have multiple tasks that depend on each other, or if you want advanced data pipeline features.

### Cons

- Heavier than cron/systemd; you’ll be installing a separate service (Airflow) or library (Prefect, Luigi).
- Might be overkill for a small set of simple scripts.

### Example: Airflow DAG (simplified)

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def upload_logs():
    # your upload code here
    pass

def edit_logs():
    # your edit code here
    pass

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 1
}

with DAG('log_pipeline',
         default_args=default_args,
         schedule_interval='@daily') as dag:

    upload_task = PythonOperator(
        task_id='upload_logs',
        python_callable=upload_logs
    )

    edit_task = PythonOperator(
        task_id='edit_logs',
        python_callable=edit_logs
    )

    upload_task >> edit_task
```

---

## 5. Containerize and Use a Container-Orchestrator (e.g., Docker Compose, Kubernetes)

### How It Works

- Put each script in a Docker container or combine them into a single container with an entrypoint that triggers your tasks.
- Schedule or continuously run them on a system like Docker Compose or Kubernetes CronJobs.

### Pros

- Great for portability and isolation.
- If you already use containers, it’s straightforward to orchestrate multiple microservices or script-based services.

### Cons

- Requires Docker or Kubernetes knowledge.
- Overhead for a simple “folder of scripts” scenario can be large unless you are already containerizing your homelab.

### Example: Docker Compose (simplified)

```yaml
version: '3'
services:
  orchestrator:
    build: .
    container_name: orchestrator
    restart: always
    volumes:
      - ./scripts:/app/scripts
    command: python /app/scripts/orchestrator.py
```

---

## 6. Use a Job Queue (Celery, RQ, etc.)

### How It Works

- Set up a message broker (e.g., Redis, RabbitMQ) and a worker system (Celery or RQ).
- Each script runs as a “task” that gets queued up and executed by workers.
- Can schedule tasks at intervals, trigger them based on events, and scale up workers if you have many tasks.

### Pros

- Great for asynchronous workloads, distributing tasks across multiple machines.
- Built-in retry, concurrency control, and monitoring tools.

### Cons

- Requires running a broker (Redis, RabbitMQ) plus at least one worker.
- More complex setup than cron or systemd.

---

## Putting It All Together

1. **Assess your needs**:
   - **Simple scheduling?** Cron or a Python scheduler (APScheduler) is usually enough.
   - **Runs on a server continuously, might need logs and restarts?** A systemd service or Docker container with a scheduler inside.
   - **Complex data pipelines or workflows?** Airflow, Luigi, or Prefect.
   - **Event-based or distributed tasks?** Celery or RQ with a message broker.

2. **Organize your scripts** into a project structure:
   - Keep them in a single directory or a Python package.
   - Possibly have a main “entrypoint” script that orchestrates the others.

3. **Logging and monitoring** are key:
   - Make sure your scripts log their activity (to files or a centralized logging system).
   - Check logs regularly to ensure everything is running smoothly and errors are caught.

4. **Consider version control** (e.g., Git) to track changes in your scripts and configurations.

---

### Example: A Minimal Orchestrator Script (for systemd or Docker)

Suppose you have multiple Python scripts in a folder. You can create a single orchestrator script that calls each script on a schedule or based on logic:

```python
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO)

def run_script(script_path):
    try:
        logging.info(f"Starting {script_path}...")
        subprocess.check_call(["python3", script_path])
        logging.info(f"Completed {script_path} successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running {script_path}: {e}")

if __name__ == "__main__":
    while True:
        # Run your scripts in sequence (or in parallel with threads if needed)
        run_script("/path/to/upload_logs.py")
        run_script("/path/to/edit_logs.py")
        
        # Sleep for 10 minutes before next iteration
        time.sleep(600)
```

Then you can run this script as a systemd service (or inside a Docker container) to keep it going all the time.

---

## Conclusion

Turning a folder of scripts into a constantly running background system generally involves **scheduling** (via cron, Python-based schedulers, or a workflow orchestrator) and possibly **daemonizing** (via systemd or Docker) to ensure it stays running indefinitely.

- For **lightweight** setups: Use **cron** or a **systemd** service.
- For more **complex** pipelines or dependencies: Consider Airflow, Luigi, or Prefect.
- For **distributed** or **event-driven** systems: Look into Celery or RQ.

Pick the simplest tool that meets your needs and gradually evolve your setup if it grows in complexity.


#### You:
<time datetime="2025-01-09T17:47:27.398Z" title="1/10/2025, 2:47:27 AM">02:47</time>

Many of these scripts depend on each other. Like script a needs to run before script b, and script c should only run in certain conditions. Is airflow a good solution for this?

#### ChatGPT:
<time datetime="2025-01-09T17:48:42.567Z" title="1/10/2025, 2:48:42 AM">02:48</time>

**Short answer:** Yes, Apache Airflow is very well-suited to orchestrating scripts that depend on each other or need to run under certain conditions. It was designed for building and managing complex workflows in which each task has prerequisites and conditional logic.

Below is a bit more detail on why Airflow is a good fit, along with some considerations.

---

## Why Airflow is a Good Fit

1. **Dependency Management**\
   Airflow jobs are defined as a Directed Acyclic Graph (DAG). Each node in the DAG is a “task” (which often corresponds to a script or function), and you can easily specify that *Task B* depends on *Task A* completing successfully before it runs. That means the scheduler will handle waiting for *Task A* to finish before kicking off *Task B*.

2. **Conditional Execution (Branching)**\
   Airflow has operators like `BranchPythonOperator` that let you define a condition. The operator decides which branch of tasks to run next. For example:
   ```python
   def condition_check(**context):
       # decide which path to follow
       if some_condition_is_true:
           return 'task_c'
       else:
           return 'task_d'

   branch_op = BranchPythonOperator(
       task_id='branch_op',
       python_callable=condition_check,
       dag=dag
   )
   ```
   Here, if `condition_check` returns `task_c`, the scheduler will proceed only with the tasks downstream of `task_c`.

3. **Built-In Scheduling**\
   You can schedule your DAG to run at certain intervals (e.g., hourly, daily) or even trigger it manually or via an API. This is more powerful than using system cron, especially when dealing with many interdependent scripts.

4. **Monitoring and Logging**\
   Airflow comes with a web UI that shows the status of each task, how long it took, and whether it succeeded or failed. You can also view logs for each task run, which helps a lot with debugging.

5. **Retries and Alerting**\
   Airflow tasks can be configured to retry on failure a certain number of times with a delay in between. You can also set up email or Slack alerts to notify you if tasks fail.

---

## Considerations

1. **Overhead**\
   Airflow is more complex than just using cron or a simple Python scheduler. It requires a backend database (often SQLite for testing, but PostgreSQL or MySQL in production) and typically a separate web server and scheduler. If your homelab environment is resource-constrained, keep in mind there’s some overhead.

2. **Setup Complexity**\
   Installing and configuring Airflow might require learning a bit about Docker or Python environment management. You’ll also want to set up some form of persistent storage for the Airflow metadata database and logs.

3. **DAG Complexity**\
   While Airflow does a great job of representing tasks as a graph, it only supports Directed Acyclic Graphs. Circular dependencies (where Task A depends on Task B, which depends on Task A, etc.) are not allowed. Most real workflows are naturally acyclic, but it’s worth noting.

4. **Learning Curve**\
   Writing Airflow DAGs is straightforward once you get the basic pattern. However, you’ll need to understand a few key concepts (DAGs, tasks, operators, hooks, etc.) and how to structure your project.

---

## Minimal Example of an Airflow DAG

Below is a tiny example DAG that shows how you might orchestrate scripts `script_a`, `script_b`, and `script_c`, with dependencies and conditions:

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from datetime import datetime

def run_script_a():
    # ... code for script a
    print("Script A is running.")

def run_script_b():
    # ... code for script b
    print("Script B is running.")

def run_script_c():
    # ... code for script c
    print("Script C is running.")

def condition_check(**context):
    # Decide if script_c should run based on some condition
    # For example, check the result from script_a or an external state
    # Return the 'task_c' task_id if we should run script C, otherwise skip
    # For simplicity, let's always run script_c
    return 'task_c'

default_args = {
    'start_date': datetime(2025, 1, 1),
    'retries': 1
}

with DAG(
    dag_id='example_dependent_scripts',
    default_args=default_args,
    schedule_interval='@daily',  # runs daily
    catchup=False,
) as dag:

    task_a = PythonOperator(
        task_id='task_a',
        python_callable=run_script_a
    )

    task_b = PythonOperator(
        task_id='task_b',
        python_callable=run_script_b
    )

    branch_op = BranchPythonOperator(
        task_id='branch_op',
        python_callable=condition_check,
        provide_context=True
    )

    task_c = PythonOperator(
        task_id='task_c',
        python_callable=run_script_c
    )

    # Dependencies:
    # A -> B -> branching -> (maybe) C
    task_a >> task_b >> branch_op >> task_c
```

- `task_a` runs first.
- After `task_a` finishes, `task_b` runs.
- After `task_b` finishes, we run `branch_op`.
- `branch_op` decides if we proceed to `task_c`. In the code above, we always go to `task_c`, but you can add real logic.

---

## Conclusion

- **Airflow** is an excellent solution for orchestrating dependent scripts, offering scheduling, logging, error handling, and a nice UI.
- It does introduce more infrastructure overhead compared to simpler tools like `cron` or a custom Python scheduler.
- If you have a homelab and want to manage a growing number of interdependent tasks with advanced logic, Airflow is worth the investment in time to learn and deploy. If your needs are very light, you might consider something simpler (like [APScheduler](https://apscheduler.readthedocs.io/en/stable/) or a custom orchestrator script).

In short, if you have multiple scripts with dependencies and conditional execution needs, and you’re comfortable setting up a small web server and a database for Airflow, it’s absolutely a good fit.


#### You:
<time datetime="2025-01-09T17:48:47.112Z" title="1/10/2025, 2:48:47 AM">02:48</time>

What are some alternatives to airflow? I have used postman flows in the past as a low-code solution

#### ChatGPT:
<time datetime="2025-01-09T17:50:22.530Z" title="1/10/2025, 2:50:22 AM">02:50</time>

There are quite a few workflow/orchestration tools and platforms out there beyond Airflow—ranging from code-heavy frameworks like Luigi or Prefect to low-code or visual solutions like n8n or Node-RED. Below is a breakdown of some popular alternatives, along with key details and considerations.

---

## 1. **Luigi**

- **What It Is**: A Python package (created by Spotify) for building complex pipelines of batch jobs.
- **Key Features**:
  - Dependency graph declaration is code-based (similar to Airflow’s DAG model).
  - Focuses on data pipelines and ensures tasks don’t run again if outputs exist (idempotent execution).
- **Pros**:
  - Pure Python, straightforward dependency model.
  - Simpler than Airflow if your needs are mostly about chaining tasks and ensuring outputs are up to date.
- **Cons**:
  - Less robust scheduling/UI than Airflow.
  - Smaller community and fewer features (no built-in UI without third-party add-ons).

---

## 2. **Prefect**

- **What It Is**: A modern workflow management system in Python, positioning itself as “Airflow 2.0.”
- **Key Features**:
  - “Flows” for orchestration and “Tasks” for logic.
  - Emphasis on a Pythonic developer experience with fewer limitations than classic Airflow.
  - Cloud (SaaS) or self-hosted (open source) options.
- **Pros**:
  - Very friendly Python API.
  - Easy to add dynamic or branching logic.
  - Well-documented, growing ecosystem.
- **Cons**:
  - Some advanced features (like the hosted UI) may require a paid plan (but there is a free tier).
  - Still relatively young compared to Airflow or Luigi, though rapidly maturing.

---

## 3. **Dagster**

- **What It Is**: Another next-generation data orchestration platform that allows you to define “ops” and “graphs” in Python.
- **Key Features**:
  - Strong focus on data quality, type-checking, and solid software engineering practices.
  - Built-in support for partitioned data, backfills, etc.
  - Has a nice web UI (Dagit) out-of-the-box.
- **Pros**:
  - Clean Pythonic API.
  - Great developer experience, especially for data engineering.
- **Cons**:
  - Similar to Prefect, it’s a newer platform with a smaller community than Airflow.
  - May be overkill if you have very simple pipelines.

---

## 4. **n8n**

- **What It Is**: A fair-code, self-hostable workflow automation tool with a visual, node-based interface.
- **Key Features**:
  - Low-code/visual approach—drag-and-drop “nodes” that can represent triggers (like webhooks, cron schedules, or external APIs) and actions (like running scripts, HTTP requests, etc.).
  - Can run in Docker, on-prem, or in the cloud.
- **Pros**:
  - Very user-friendly and easy to set up.
  - Great for orchestrating APIs, webhooks, and other event-driven tasks.
- **Cons**:
  - Less “Python-centric” than Airflow—if you rely on running Python scripts with complex data pipelines, you might need more configuration.
  - Not as robust for large-scale data engineering tasks (though it can still be used for simpler workloads).

---

## 5. **Node-RED**

- **What It Is**: A low-code visual tool originally developed by IBM for wiring together hardware devices, APIs, and services.
- **Key Features**:
  - Node-based flow editor that runs in Node.js.
  - Great for IoT projects, simple API-based automations, or quick prototypes.
- **Pros**:
  - Very easy for non-developers or those who prefer a drag-and-drop UI.
  - Large community of contributed “nodes” for different integrations.
- **Cons**:
  - Not specialized for data pipelines in Python (like Airflow).
  - Complex, multi-step orchestration logic can become tricky to manage visually.

---

## 6. **Jenkins** / **GitHub Actions** / **GitLab CI**

- **What They Are**: Primarily CI/CD tools, but can be used for general task automation or orchestration.
- **Key Features**:
  - Pipelines can define steps and dependencies.
  - Schedules or triggers (e.g., code commits) can kick off pipelines.
- **Pros**:
  - If you already have Jenkins or a CI tool in your environment, it may be simpler to reuse.
  - Good ecosystem for automating builds, tests, etc.
- **Cons**:
  - Less intuitive for data-focused workflows or job scheduling that isn’t tied to code commits.
  - Lacks some of the advanced features of Airflow for complex dependencies and big data orchestration.

---

## 7. **Argo Workflows**

- **What It Is**: A Kubernetes-native workflow engine.
- **Key Features**:
  - Defines workflows as YAML specs, each step is a container.
  - Scales natively on Kubernetes—great for containerized tasks.
- **Pros**:
  - Very powerful if you already use Kubernetes.
  - Can handle large-scale parallel tasks.
- **Cons**:
  - Requires Kubernetes expertise.
  - More infrastructure overhead for a simple homelab.

---

## 8. **AWS Step Functions / Azure Data Factory / Google Cloud Composer**

- **What They Are**: Cloud vendor-specific orchestration solutions.
- **AWS Step Functions** orchestrates serverless services; **Azure Data Factory** orchestrates pipelines in Azure; **Google Cloud Composer** is basically a managed Airflow instance.
- **Pros**:
  - If you’re already all-in on a cloud platform, these are well-integrated with other services.
  - Lower overhead if you don’t want to manage infrastructure.
- **Cons**:
  - Cloud lock-in.
  - Might not be ideal for a homelab unless you want a hybrid approach.

---

## Comparison to Postman Flows

**Postman Flows** is a relatively lightweight, low-code way to chain API calls together and build simple “workflows” inside Postman. It’s good for simple API-based automation, but:

1. It’s primarily a **tool for testing and demoing APIs** rather than a long-running production orchestrator.
2. It’s not as full-featured in terms of scheduling, retry logic, or robust error handling.
3. Managing dependencies between many complex scripts might get cumbersome as flows become large.

If you already like the low-code, node-based approach of Postman Flows, you might feel more at home with **n8n** or **Node-RED**, which offer a similar visual approach but are more robust for orchestrating recurring tasks.

---

## Choosing the Right Tool

1. **Simple “I just need scheduling and a few dependencies”:**
   - **Cron** (or Windows Task Scheduler) + scripting, or a minimal Python orchestrator.
2. **Low-code environment for API calls and event-driven tasks:**
   - **n8n** or **Node-RED**.
3. **Python-based data pipelines with some complexity:**
   - **Luigi** (lighter) or **Airflow** / **Prefect** (more advanced).
4. **Production-grade orchestration with a nice UI, many features:**
   - **Airflow**, **Prefect**, or **Dagster**.
5. **Kubernetes-native, container-based workflows:**
   - **Argo Workflows**.

If you’re looking specifically for a **low-code** solution that also helps orchestrate Python scripts with dependencies, try something like **n8n**. If you need a more robust “pipeline” mindset (especially if you’re used to Airflow’s DAG approach), then check out **Dagster** or **Prefect** for a modern alternative.

---

### Key Takeaways

- **Yes, Airflow is powerful**, but it’s not the only game in town.
- For **low-code** solutions, consider n8n, Node-RED, or other visual flow tools.
- For **pure Python** orchestration with built-in scheduling and advanced features, consider Luigi, Prefect, or Dagster.
- For **CI/CD** style orchestration, Jenkins or GitHub Actions can be adapted.

Each tool has its pros and cons—so choose based on your environment, skill set, and the complexity of your workflows.


#### You:
<time datetime="2025-01-09T18:02:32.754Z" title="1/10/2025, 3:02:32 AM">03:02</time>

I'm really after orchestrating agentic LLMs to accomplish tasks for me, so this framework looks good. What do you think?
---
Write

Sign in
The Rise of Intelligent Agents: Exploring the Levels of Agentic Platforms
Raphael Mansuy

Raphael Mansuy
·

Follow
13 min read
·
May 9, 2024

The Rise of Intelligent Agents: Exploring the Levels of Agentic Platforms

LLM-powered Agentic Platforms could mark a significant advancement in the field of artificial intelligence, harnessing the power of Large Language Models (LLMs) to create highly sophisticated and interactive agents. These platforms enable the development of intelligent agents capable of understanding, reasoning, and engaging in natural conversations, providing accurate and context-aware assistance across a wide range of domains.

Agentic Platforms can be described through multiple levels, each building upon the capabilities of the previous one and introducing new features and functionalities.

    From the foundational Level 1 to the highly advanced Level 7, each level offers unique components, characteristics, and practical applications.

This article will explore the different levels of Agentic Platforms, delving into the key aspects that define each level and showcasing their potential impact on various industries and use cases. By understanding these levels, we can gain a comprehensive understanding of the evolving capabilities of LLM-powered agents and their potential to revolutionize the way we interact with and leverage artificial intelligence.
Level 1: Foundation

The first level of an Agentic Platform lays the groundwork for creating a conversational agent. It consists of three key components:

    Custom System Prompt: A carefully designed prompt that sets the context and guides the behavior of the LLM. It defines the agent’s purpose, personality, and communication style.
    LLM Model: A pre-trained language model, which generates human-like responses based on the input prompt and its vast knowledge acquired during training.
    Configuration: Fine-tuned settings, including temperature and maximum token count, that control the randomness and verbosity of the generated responses, allowing for a more natural and coherent conversation.

Level 1 Agentic Platforms provide a solid foundation for creating engaging and informative conversational agents.
Level 2: Knowledge Augmentation

Building upon the capabilities of Level 1, the second level introduces a knowledge base to enhance the agent’s understanding and responsiveness. The main components of a Level 2 Agentic Platform include:

    Custom System Prompt and LLM Configuration: The foundation from Level 1 remains crucial for guiding the agent’s behavior and generating appropriate responses.
    Knowledge Base: A curated collection of documents, articles, and other relevant information sources that are organized and indexed to provide additional context and domain-specific knowledge to the LLM.

When a user interacts with a Level 2 Agentic Platform, the agent not only relies on the LLM’s pre-trained knowledge but also draws upon the information stored in the knowledge base. This allows the agent to provide more accurate, relevant, and informative responses tailored to the user’s specific needs and context.
Level 3: Tool-Assisted Intelligence with Code Execution

The third level of Agentic Platforms takes the capabilities of Level 2 to new heights by integrating various tools, APIs, and a code execution tool. The key components of a Level 3 platform include:

    Custom System Prompt, LLM Configuration, and Knowledge Base: The foundation and knowledge augmentation from previous levels remain essential for the agent’s performance. The system prompt and LLM configuration are further enhanced to support the integration of external tools, APIs, and the code execution tool.
    Tool Integration: Level 3 Agentic Platforms incorporate a range of tools and APIs to expand the agent’s abilities and access to real-time information. These tools can include search APIs for retrieving web-based information, database query APIs for accessing structured data, and other external services for performing specific tasks or computations.
    Code Execution Tool: A distinguishing feature of Level 3 Agentic Platforms is the integration of a code execution tool. This tool allows the agent to execute code snippets or scripts in various programming languages, such as Python, JavaScript, or SQL. The code execution tool enables the agent to perform complex computations, data manipulations, and custom logic based on user inputs or predefined scripts.

When a user interacts with a Level 3 Agentic Platform, the agent can leverage its own knowledge, the information stored in the knowledge base, the integrated tools, and the code execution tool to provide comprehensive, up-to-date, and actionable responses. For example, a Level 3 data analysis agent can use a database query API to retrieve relevant data, execute Python scripts to perform statistical analysis or data visualization, and provide insights and recommendations based on the results.

The code execution tool empowers Level 3 Agentic Platforms to go beyond simple information retrieval and perform complex tasks that require computational power and custom logic. The agent can execute pre-written scripts or dynamically generate code based on user inputs and requirements. This capability opens up a wide range of possibilities for data processing, automation, and problem-solving.

For instance, consider a Level 3 financial analysis agent. A user can provide a dataset containing financial transactions and ask the agent to perform a specific analysis, such as calculating the return on investment (ROI) for different investment options. The agent can use the code execution tool to run a Python script that reads the dataset, performs the necessary calculations, and generates a report with the ROI for each investment option. The agent can then provide the user with the generated report and offer insights and recommendations based on the analysis.

The code execution tool also enables Level 3 Agentic Platforms to handle tasks that require iterative or conditional logic. For example, a user can ask the agent to find the optimal route between multiple locations based on certain constraints, such as distance, time, or cost. The agent can execute a JavaScript script that implements a routing algorithm, considering the provided constraints and using external APIs to retrieve real-time traffic data or transportation information. The agent can then present the user with the optimal route and provide step-by-step directions.

Level 3 Agentic Platforms with code execution capabilities offer immense flexibility and power in handling complex tasks and computations. The integration of tools, APIs, and the code execution tool allows agents to leverage the best of both pre-built functionality and custom logic. This level of tool-assisted intelligence empowers agents to provide highly sophisticated and tailored solutions to user queries, automate complex workflows, and solve problems that require computational expertise.

However, it’s important to note that the code execution tool should be used with appropriate security measures and safeguards in place. The agent should have well-defined permissions and limitations on the code it can execute to prevent potential misuse or security risks. Additionally, the code execution tool should be monitored and audited regularly to ensure the integrity and reliability of the executed code.

In summary, Level 3 Agentic Platforms with tool-assisted intelligence and code execution capabilities offer a powerful combination of knowledge, external tools, and computational power. By leveraging the code execution tool, agents can perform complex tasks, automate workflows, and provide highly customized solutions to user queries. This level of intelligence enables organizations to tackle a wide range of challenges and drive innovation across various domains.
Level 4: Multi-Modal Interaction

At this level, the Agentic Platform expands its communication capabilities beyond text-based interactions. The key components of a Level 4 platform include:

    Multi-Modal Input: The agent can understand and process input from various modalities, such as voice, images, and videos, in addition to text.
    Multi-Modal Output: The agent can generate responses in different formats, including text, speech, images, and videos, to provide a more engaging and interactive user experience.
    Cross-Modal Understanding: The agent can correlate and integrate information from different modalities to gain a more comprehensive understanding of the user’s intent and context.

Level 4 Agentic Platforms enable more natural and intuitive interactions, allowing users to communicate with the agent using their preferred modality and receive responses in the most appropriate format.
Level 5: Personalization and Adaptation with Memory Integration

At Level 5, the Agentic Platform incorporates advanced personalization and adaptation capabilities, leveraging both short-term and long-term memory to provide a more seamless and context-aware user experience. The key components of a Level 5 platform include:

    User Profiling with Long-Term Memory: The agent can create and maintain comprehensive user profiles based on their interactions, preferences, and behavior over an extended period. This long-term memory allows the agent to understand and anticipate user needs, providing more personalized and proactive assistance.
    Contextual Awareness with Short-Term Memory: The agent can understand and adapt to the user’s current context by leveraging short-term memory. It can keep track of recent interactions, conversation history, and real-time situational data, such as location, time, and device, to provide more relevant and timely responses. The short-term memory enables the agent to maintain continuity and coherence throughout the conversation.
    Continuous Learning and Memory Consolidation: The agent can learn from user feedback and interactions in real-time, updating its short-term memory accordingly. Over time, the agent consolidates the most relevant and frequently accessed information from its short-term memory into its long-term memory. This continuous learning process allows the agent to refine its understanding of individual users and improve its performance based on their unique needs and preferences.
    Memory-Driven Personalization: By combining the insights from both short-term and long-term memory, the agent can deliver highly personalized experiences. It can draw upon the user’s long-term preferences and interests while considering the current context and recent interactions to provide tailored recommendations, anticipate needs, and offer proactive support.
    Seamless Context Switching: With the integration of short-term and long-term memory, the agent can handle multiple tasks and conversations concurrently. It can switch between different contexts and users effortlessly, maintaining a clear understanding of each interaction’s history and context. This allows for a more natural and efficient user experience, as the agent can quickly resume previous conversations and tasks without losing track of important details.

Level 5 Agentic Platforms with memory integration offer a highly personalized and adaptive experience, leveraging both short-term and long-term memory to provide contextually relevant and proactive assistance. By continuously learning from user interactions and consolidating knowledge over time, these agents can develop a deep understanding of individual users, anticipate their needs, and deliver tailored support that evolves alongside the user’s changing requirements and preferences.
Level 6: Workflow-Driven Task Automation with Human-in-the-Loop

At Level 6, Agentic Platforms introduce a workflow-driven approach to task automation, enabling users to define and execute complex tasks using a no-code interface. Additionally, Level 6 platforms incorporate human-in-the-loop functionality to allow for human intervention, decision-making, and collaboration at key points within the workflow. The key components of a Level 6 platform include:

    Workflow Designer: Level 6 Agentic Platforms provide a user-friendly, no-code interface called the Workflow Designer. This visual tool allows users to define and design workflows for specific tasks using a drag-and-drop interface. Users can create a series of steps, decision points, conditional branches, and human intervention points to define the logic and flow of the task execution without requiring any programming knowledge.
    Workflow Representation: The designed workflow is represented as a graph or a state machine, clearly depicting the steps, transitions, decision points, and human intervention points involved in the task. Each node in the graph or state in the state machine represents a specific action, decision, or human input, while the edges or transitions define the flow and dependencies between the steps. This visual representation helps users understand and visualize the task execution process.
    Agent Integration: Level 6 Agentic Platforms integrate agents from previous levels (Level 1 to Level 5) to execute specific steps within the workflow. Each step in the workflow can be assigned to an appropriate agent based on the required capabilities and knowledge. For example, a Level 1 agent can handle simple data retrieval or formatting tasks, while a Level 3 agent can perform more complex actions that require external tool integration or knowledge base access.
    Human Intervention Points: Level 6 Agentic Platforms introduce human intervention points within the workflow. These points represent specific steps or decision points where human input, judgment, or approval is required. Users can define the criteria or conditions that trigger human intervention, such as handling exceptions, making critical decisions, or providing domain expertise. When a human intervention point is reached during workflow execution, the platform notifies the designated human user and waits for their input before proceeding.
    Collaboration and Communication: Level 6 Agentic Platforms facilitate collaboration and communication between human users and agents involved in the workflow. The platform provides interfaces and tools for human users to review the workflow progress, provide input, and communicate with the agents. This collaboration ensures that human expertise and decision-making are incorporated into the automated process, allowing for a more comprehensive and context-aware task execution.
    Workflow Execution with Human-in-the-Loop: When a user initiates a task through the Level 6 Agentic Platform, the corresponding workflow is triggered. The platform orchestrates the execution of the workflow, following the defined steps and transitions. It coordinates the actions of the assigned agents and handles human intervention points as defined in the workflow. When a human intervention point is reached, the platform notifies the designated human user and waits for their input. Once the human input is received, the workflow resumes execution, incorporating the human decision or action into the automated process.
    Monitoring and Reporting: Level 6 Agentic Platforms offer monitoring and reporting capabilities to track the progress and performance of workflow executions, including human intervention points. Users can view real-time status updates, execution logs, and metrics related to the tasks, as well as the history of human interventions and decisions. This allows for transparency, accountability, and continuous improvement of the automated processes.

By incorporating human-in-the-loop functionality, Level 6 Agentic Platforms enable a collaborative and adaptive approach to task automation. The integration of human expertise and decision-making at key points within the workflow ensures that the automated process remains aligned with business objectives, handles exceptions effectively, and leverages human judgment when necessary.

For example, consider a Level 6 Agentic Platform deployed in a loan approval process. The Workflow Designer can be used to create a workflow that automates the loan application review and decision-making process. The workflow might include steps such as:

    Receiving the loan application through various channels (online, in-person, mail)
    Assigning the application to a Level 2 agent for initial data extraction and verification
    Routing the application to a Level 3 agent for credit score analysis and risk assessment
    Introducing a human intervention point for a loan officer to review the application and make a final decision based on the agent’s analysis and recommendations
    Communicating the loan decision to the applicant and initiating the next steps (loan disbursement or rejection)

At the human intervention point, the loan officer receives a notification to review the loan application. The officer can access the workflow progress, review the agent’s analysis and recommendations, and make a final decision based on their expertise and judgment. The officer’s decision is then incorporated back into the workflow, triggering the appropriate next steps.

Throughout the workflow execution, the platform monitors the progress, including the human intervention points, and provides real-time updates to the relevant stakeholders. The history of human interventions and decisions is recorded for auditing and continuous improvement purposes.

By leveraging workflow-driven task automation with human-in-the-loop functionality, Level 6 Agentic Platforms enable organizations to strike a balance between automation and human expertise. The integration of human decision-making and collaboration at critical points within the workflow ensures that the automated process remains aligned with business objectives, handles exceptions effectively, and incorporates domain knowledge when necessary. This collaborative approach enhances the efficiency, accuracy, and adaptability of task execution, while maintaining the necessary level of human oversight and control.
Level 7: Dynamic Workflow Orchestration

At Level 7, the Agentic Platform introduces an Orchestrator agent that dynamically creates and adapts workflows to accomplish tasks based on the specific requirements and context. This level differs from the previous level (Level 6) where the workflows were predefined. The key components and characteristics of a Level 7 platform include:

    Orchestrator Agent: The Orchestrator agent is a high-level, intelligent agent responsible for analyzing the task requirements, understanding the context, and dynamically creating a workflow to accomplish the task. It possesses advanced reasoning, planning, and decision-making capabilities to determine the optimal sequence of steps and the appropriate agents to involve in the workflow.
    Dynamic Workflow Generation: Instead of relying on predefined workflows, the Orchestrator agent dynamically generates workflows on-the-fly based on the specific task at hand. It considers factors such as the task complexity, available resources, time constraints, and dependencies to create a tailored workflow that efficiently achieves the desired outcome.
    Contextual Understanding: The Orchestrator agent has a deep understanding of the task context, including the user’s intent, preferences, and constraints. It leverages this contextual knowledge to make informed decisions while creating the workflow, ensuring that the generated workflow aligns with the user’s expectations and requirements.
    Agent Coordination: The Orchestrator agent identifies and coordinates the actions of various agents (Level 1, 2, or 3) required to execute the dynamically generated workflow. It assigns tasks to the appropriate agents based on their capabilities, availability, and performance metrics. The Orchestrator agent manages the communication and data flow between the agents, ensuring seamless collaboration and information sharing.
    Adaptive Workflow Refinement: As the workflow execution progresses, the Orchestrator agent continuously monitors the progress and adapts the workflow based on real-time feedback and changing circumstances. It can dynamically adjust the workflow steps, reassign tasks to different agents, or introduce additional steps to handle unexpected challenges or optimize the overall performance.
    Learning and Optimization: The Orchestrator agent learns from each workflow execution and uses this knowledge to improve future workflow generation and optimization. It analyzes the outcomes, performance metrics, and user feedback to identify patterns, best practices, and areas for improvement. Over time, the Orchestrator agent becomes more efficient and effective in creating workflows that deliver optimal results.
    Explainable Workflow: The Orchestrator agent provides transparency and explainability in the generated workflows. It can present the reasoning behind the chosen steps, agent assignments, and adaptations made during the workflow execution. This transparency helps users understand and trust the dynamically generated workflows, facilitating collaboration and decision-making.

Level 7 Agentic Platforms with Dynamic Workflow Orchestration offer a highly adaptive and intelligent approach to task automation. By leveraging an Orchestrator agent to dynamically create and refine workflows based on the specific task requirements and context, these platforms enable more flexible and efficient task execution. The Orchestrator agent’s ability to understand the context, coordinate agents, and adapt workflows in real-time sets it apart from the predefined workflow approach of Level 7.

This level empowers organizations to handle complex, dynamic, and unpredictable tasks that require intelligent planning and adaptation. The Orchestrator agent’s ability to learn and optimize workflows over time leads to continuous improvement and enhanced performance, making Level 7 Agentic Platforms a powerful tool for tackling evolving business challenges and driving innovation.
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
Artificial Intelligence
Agents
Software Development

Raphael Mansuy
Written by Raphael Mansuy
831 Followers
·
2K Following

LinkedIn Top Voice for AI, Data Architecture & Data Engineering 👉 Follow me for deep dives on data-engineering and AI !
No responses yet

What are your thoughts?

Also publish to my profile
More from Raphael Mansuy
DuckDB for the Impatient: From Novice to Practitioner in Record Time
Raphael Mansuy

Raphael Mansuy
DuckDB for the Impatient: From Novice to Practitioner in Record Time
A comprehensive guide to mastering DuckDB, an in-process SQL OLAP database optimized for analytical queries.
Sep 23, 2024
58
1
Building a Coding Agent with the Quantalogic ReAct Framework: A Step-by-Step Guide
Raphael Mansuy

Raphael Mansuy
Building a Coding Agent with the Quantalogic ReAct Framework: A Step-by-Step Guide
In this tutorial, we’ll walk through the process of building a coding agent using the Quantalogic ReAct Framework.
2d ago
Mastering Rust: The Ultimate Example-Driven Tutorial
Raphael Mansuy

Raphael Mansuy
Mastering Rust: The Ultimate Example-Driven Tutorial
1. Introduction to Rust
Mar 26, 2024
55
1
Bridging the Gap Between Symbolic AI and Large Language Models
AI Mind

In

AI Mind

by

Raphael Mansuy
Bridging the Gap Between Symbolic AI and Large Language Models
As an AI practitioner, I have witnessed firsthand the strengths and limitations of different approaches to artificial intelligence. In…
Aug 15, 2023
168
3
See all from Raphael Mansuy
Recommended from Medium
@created by Rahul Bhatia (author)
Artificial Intelligence in Plain English

In

Artificial Intelligence in Plain English

by

Rahul Bhatia
Building Smart AI Agents
Understanding the ReAct Pattern with Python
6d ago
138
1
How Jupyter Agent Blew My Mind. The AI Revolution You Didn’t See Coming.
AI Advances

In

AI Advances

by

Savvas Theocharous
How Jupyter Agent Blew My Mind. The AI Revolution You Didn’t See Coming.
Easily accessible, but hard to believe. Once you get your hands on it you will see what I am talking about!
Dec 31, 2024
1.3K
29
Lists
A phone with a tweet on it describing a deepfake video of the Ukrainian president, with a labeled fake image in the background
AI Regulation
6 stories·669 saves
AI-generated image of a cute tiny robot in the backdrop of ChatGPT’s logo
ChatGPT
21 stories·938 saves
General Coding Knowledge
20 stories·1853 saves
Generative AI Recommended Reading
52 stories·1591 saves
Master Agentic AI: A Beginner’s Step-by-Step Guide with SuperAgentX — Tutorial Series (Part 1)
Prabhu Raghav

Prabhu Raghav
Master Agentic AI: A Beginner’s Step-by-Step Guide with SuperAgentX — Tutorial Series (Part 1)
Hello Everyone, Welcome to the Agent AI Tutorial Series — Part 1! 🚀
Nov 20, 2024
231
1
The Anatomy of Agentic AI
Ali Arsanjani

Ali Arsanjani
The Anatomy of Agentic AI
In this article we will elaborate on the anatomy of Agentic AI and how it operates.
Jun 6, 2024
588
5
🚀Building Multi-Agent LLM Systems with PydanticAI Framework: A Step-by-Step Guide To Create AI…
GoPenAI

In

GoPenAI

by

Sreedevi Gogusetty
🚀Building Multi-Agent LLM Systems with PydanticAI Framework: A Step-by-Step Guide To Create AI…
Pydantic, a powerhouse in the Python ecosystem with over 285 million monthly downloads, has been a cornerstone of robust data validation in…
5d ago
147
2
What Are AI Agents? Your Step-by-Step Guide to Build Your Own.
CodeX

In

CodeX

by

Maximilian Vogel
What Are AI Agents? Your Step-by-Step Guide to Build Your Own.
The next big thing? Gartner believes AI agents are the future. OpenAI, Nvidia and Microsoft are betting on it — as are companies such as…
Dec 28, 2024
878
15
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


----
ControlFlow home pagedark logo

    PrefectHQ/ControlFlow
    1052
    79

Documentation
Examples
AI Glossary
Code
Community
ControlFlow Features

    Dependent Tasks
    Custom Tools
    Multi-LLM Workflows
    Private Flows
    Using Memory
    Early Termination

Core LLM Operations

    Sentiment Classifier
    Headline Categorization
    Named Entity Recognition
    Text Summarization
    Standardize Place Names
    Generate User Profiles
    Text Translation
    Data Anonymization
    Code Explanation

Agentic Flows

    Interactive Language Tutor
    Rock, Paper, Scissors
    Seinfeld Conversation
    Customer Call Routing
    Software Engineer

ControlFlow Features
Custom Tools

Provide tools to expand agent capabilities.

In ControlFlow, tools can be assigned at different levels of your workflow: to the flow itself, to specific agents, or to individual tasks. This flexibility allows you to expand agent capabilities and create more powerful workflows.

This example demonstrates how to assign and use tools at each level for a file search and information retrieval scenario, using a temporary directory with test files.

The agent in this example can read files on your local file system. While simple precautions are taken to restrict the agent to demo data created specifically for this example, you may consider this a potential security risk.
​
Code

In this example, we create an agentic workflow that searches through files looking for important information. To avoid interfering with your local file system, we’ll create a context manager that sets up a temporary directory with demo files that the agent can search.

This example’s code is split into multiple blocks for legibility. Please run each code block in sequence to run the full example.
​
Set up example data

First, let’s create a context manager that sets up a temporary directory with test files:
Files

import contextlib
import tempfile
import os

@contextlib.contextmanager
def setup_test_environment():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        files = {
            "report.txt": "This report contains important findings from our recent project...",
            "meeting_notes.txt": "In today's important meeting, we discussed the new product launch...",
            "todo.txt": "Important tasks for this week: 1. Client meeting, 2. Finish report...",
        }
        for filename, content in files.items():
            with open(os.path.join(temp_dir, filename), 'w') as f:
                f.write(content)
        
        yield temp_dir

​
Set up tools

Next, let’s create some tools for our agent to use. We have one tool for listing the files in a directory, one for reading the contents of a file, and one for printing a message to the user.

Note that tools can be any Python function, and work best when they have clear type annotations and docstrings.
Tools

def list_files(directory: str) -> list[str]:
    """List files in the given directory."""
    return os.listdir(directory)

def read_file(filepath: str) -> str:
    """Read the contents of a file from an absolute filepath."""
    with open(filepath, 'r') as file:
        return file.read()

def update_user(message: str) -> None:
    """Print a status message for the user to read."""
    print(f"[User Notification]: {message}")
    return 'User updated.'

​
Build a flow

Finally, let’s build a workflow. In this example, we want to illustrate the different ways that tools can be provided, so:

    The flow is given the update_user tool, so any agent can post a message to the user at any time
    The agent is given the list_files tool, so this agent can list files at any time
    The task is given the read_file tool, so that capability is only available while that task is running

Now, let’s build a flow that explores those files. Note that the context manager from the previous code block is used in this example to set up the example data:

import controlflow as cf

agent = cf.Agent(name="FileSearcher", tools=[list_files])


@cf.flow(tools=[update_user], default_agent=agent)  
def file_search_flow(query: str, directory: str):

    # Task 1: Find files containing the search term
    found_files = cf.Task(
        f"Identify files in the directory '{directory}' that might "
        f"relate to'{query}' and return a list of paths.",
        result_type=list[str]
    )

    # Task 2: Analyze file contents and report findings
    cf.run(
        f"Analyze the contents of the files for information related "
        "to the search term.",
        instructions='You must update the user on all your findings to complete the task.',
        tools=[read_file],
        depends_on=[found_files],
        result_type=None  # We don't need a return value as we're printing directly to the user
    )

# Run the flow within our test environment
with setup_test_environment() as temp_dir:
    file_search_flow(query="launch meeting", directory=temp_dir)

​
Key points

    Tool assignment: Tools can be assigned to flows, agents, and tasks, which lets you control which agents or tasks have access to which tools.

    Instructions: Agents will follow instructions, including how to use tools.

    Dependent tasks: The second task in this flow depends on the first task, which means 1) it automatically has visibility into its result and 2) ControlFlow automatically ran the first task when the second task was run.

    Flow context: The query parameter was part of the flow context, which means all tasks could see it even it if wasn’t explicitly provided to them.

​
Further reading

    For more details on creating and using tools, see the Tools documentation.
    To learn more about agents and their capabilities, check out the Agents guide.
    For information on how ControlFlow manages task execution and context, refer to the Running tasks guide.

By strategically assigning tools at different levels in your ControlFlow workflows, you can significantly expand the capabilities of your AI agents, enabling them to interact with external systems and perform complex operations.
Dependent Tasks
Multi-LLM Workflows
github
slack
Powered by Mintlify
On this page

    Code
    Set up example data
    Set up tools
    Build a flow
    Key points
    Further reading

Custom Tools - ControlFlow

#### ChatGPT:
<time datetime="2025-01-09T18:04:11.365Z" title="1/10/2025, 3:04:11 AM">03:04</time>

It looks like you’ve found a solid, *agentic* framework for orchestrating LLMs that can do multi-step tasks and even call external tools/code. Below are some thoughts on where this approach fits in, why it’s appealing, and how it compares to other agentic or workflow frameworks.

---

## 1. Why This Agentic “Levels” Model Is Interesting

1. **Structured Maturity Model**: The seven levels (foundation, knowledge augmentation, code execution, multi-modal, memory-driven personalization, workflow automation, dynamic orchestration) give you a conceptual roadmap of how an LLM-based agent might evolve from a simple chatbot to a fully dynamic orchestrator that can stitch together tasks and tools on the fly. It’s similar to how machine learning teams describe ML “maturity” (from ad hoc scripts to fully automated pipelines).

2. **Clear Feature Progression**: Each level adds a major capability:
   - **Level 3** (Tool-Assisted Intelligence): The ability to call APIs or run code means your agent is no longer just answering queries—it’s *acting* on your behalf.
   - **Level 6** (Workflow-Driven with Human-in-the-Loop): This is perfect for tasks that you can mostly automate but still need human approval at key decision points (e.g., finance, compliance, healthcare).
   - **Level 7** (Dynamic Workflow Orchestration): The agent can figure out *on its own* how to chain tasks, tools, and sub-agents. It’s the holy grail of “autonomous agents” but also the highest complexity.

---

## 2. How This “ControlFlow” Example Aligns

The snippet you shared about **ControlFlow** (apparently from a PrefectHQ repo or a similar AI orchestration library) demonstrates:

- **Flows with Tools**: The ability to assign tools at the flow, agent, or task level. This is basically a “Level 3 or 4” type scenario—an agent that can read files, list files, notify the user, etc.
- **Dependent Tasks**: The second step depends on the first step’s output. This is a hallmark of a workflow engine.
- **Agent + Tools** + (Potential) **LLM**: Although the example itself is fairly simple (reading from a directory), you can see how you could plug in an LLM to do natural language queries, searching across knowledge bases, or generating code on the fly.

You can think of **ControlFlow** as an orchestration layer that:

1. Lets you define multi-step flows (like in Prefect or Airflow).
2. Wraps LLM calls in tasks, giving them the ability to use “tools” (Python functions, APIs, file I/O, etc.).
3. Keeps track of dependencies (so each step can see the output from the previous step).

That’s very much the direction the “Level 3 to 6” agentic model is describing.

---

## 3. Comparisons to Other Agentic Frameworks

1. **LangChain**
   - Popular library for building “LLM apps” that do chain-of-thought prompting, tool usage, and memory (Levels 3–5).
   - Integrates many external APIs and vector DBs, so you can easily augment knowledge or run code.
   - Doesn’t have built-in *workflow orchestration*—you often rely on your own Python or a separate orchestrator (like Airflow, Prefect, etc.).

2. **Haystack**
   - Primarily used for search/Q\&A over documents, but can incorporate LLMs, knowledge bases, and custom “nodes” in a pipeline.
   - Good for Level 2 knowledge augmentation and some basic chaining.

3. **PydanticAI or ReAct-based Agents**
   - Libraries that implement the ReAct pattern (Reason + Act) with LLMs.
   - Great for hooking LLM reasoning into tool use, but often you still need an external orchestrator to handle multi-step workflows, scheduling, user approvals, etc.

4. **n8n / Node-RED**
   - Visual, low-code automation tools.
   - Great for hooking up multiple steps and calling out to APIs, but not deeply specialized in chain-of-thought or advanced LLM memory.
   - Good if you want a flowchart style UI with some LLM steps sprinkled in.

5. **Airflow / Prefect**
   - Traditional workflow orchestrators for data pipelines, also used for LLM pipelines.
   - You can embed agent logic (or call out to it) in tasks.
   - Very robust scheduling, logging, monitoring, retries.
   - Typically you add LLM “agentic” behavior *within* the tasks rather than having the orchestrator itself be “agentic.”

---

## 4. Why This Looks Good for “Agentic Orchestration”

- **Low overhead** (compared to building everything from scratch).
- **Workflow + LLM** out of the box: You get the best of both worlds—structured tasks (with dependencies) *and* an LLM agent that can dynamically decide how to use the assigned tools.
- **Human-in-the-loop** is baked in: As you progress to “Level 6,” you can embed approval steps or manual interventions for critical tasks.
- **Fine-grained control over tools**: By scoping tools to a flow, an agent, or a single task, you limit what the LLM can do at each point. This is great for security (you don’t want your LLM reading random files on your system outside the intended directory).

---

## 5. Best Practices & Caveats

1. **Security**:
   - Any time you let an LLM call arbitrary code or read arbitrary files, you need *sandboxes* or tight scoping. The example’s use of a temporary directory is a step in the right direction, but you’ll still want to carefully control what the agent can access.

2. **Prompt / System Prompt Design**:
   - If you’re letting the LLM coordinate tasks and call tools, you’ll need robust prompts that set boundaries and instruct the LLM how to handle edge cases.
   - Otherwise, you might get unexpected or suboptimal behaviors (e.g., the LLM tries to parse a huge file in one shot).

3. **Observability**:
   - Consider storing logs, outputs, and user interactions in a database or platform like Prefect/Airflow for historical tracking.
   - This is especially important if your agent is doing “Level 6 or 7” tasks that affect real systems or handle important data.

4. **Maintain a Clear “Memory” Strategy**:
   - As soon as you want personalization, short- or long-term memory, you’ll need to incorporate a vector database or some other memory store. This typically happens around “Level 5.”
   - The framework you’re using (ControlFlow) may have built-in support for memory or let you plug in your own.

---

## 6. Final Thoughts

- **Yes, this framework looks great** if you want to orchestrate an LLM that can do multi-step workflows, use external tools, and coordinate tasks.
- It’s a nice sweet spot between a simple library (like just using LangChain in Python) and a full-blown workflow engine (Airflow/Prefect) with minimal LLM awareness.
- As you scale up or move to heavier production needs (e.g., complicated scheduling, multiple concurrent flows, strict SLAs), you might still integrate this agentic approach with a more classical orchestrator—sometimes people will embed agentic flows *inside* bigger data pipelines.

Overall, **an agentic, tool-using LLM orchestrator** like the one shown is *exactly* the kind of architecture you need if your goal is to let LLMs autonomously accomplish tasks. It’s got built-in safety rails (scoped tools), human-in-the-loop points, and the ability to chain multiple steps, which aligns well with the “Level 3+” agentic maturity model you referenced. If the usage model and development style fit your team’s workflow, it’s absolutely worth exploring further.


#### You:
<time datetime="2025-01-09T18:10:39.607Z" title="1/10/2025, 3:10:39 AM">03:10</time>

Exellent. Help me set up this agentic system from level 1 through level 7. Before we start. Tell me whaat you know about multi agent systems

#### ChatGPT:
<time datetime="2025-01-09T18:11:46.954Z" title="1/10/2025, 3:11:46 AM">03:11</time>

Multi-agent systems (MAS) are collections of autonomous, interacting entities—often called “agents”—that work together (or sometimes compete) to accomplish tasks, make decisions, or solve complex problems. Each agent typically has its own goals, knowledge, and capabilities, and can adapt its behavior based on the environment or interactions with other agents. Although multi-agent systems originated in the fields of AI and distributed computing, they’ve become increasingly relevant for Large Language Models (LLMs) as well, enabling powerful workflows where multiple specialized LLM “agents” collaborate to handle different aspects of a larger task.

Below are a few key concepts about multi-agent systems, especially in the context of LLMs:

1. **Autonomy**\
   Each agent operates independently, deciding what actions to take without direct human micromanagement. In an LLM scenario, this means each agent can interpret prompts and produce responses, call tools, or solve sub-problems without constant external oversight.

2. **Decentralization**\
   Multi-agent systems often have no single “central” controller. Instead, they rely on coordination protocols, message passing, or well-defined roles that let agents communicate and synchronize. Even if there is a higher-level “orchestrator” or “manager,” the agents themselves still have localized decision-making power.

3. **Communication and Coordination**\
   Agents typically communicate via messages or shared memory. In LLM-based systems, this might translate to specialized prompts or context windows that let agents pass partial results, ask each other questions, or delegate tasks.

4. **Cooperation vs. Competition**
   - **Cooperative MAS**: Agents aim to work collaboratively, often sharing knowledge or partial results to achieve a common goal (e.g., summarizing a long document by splitting it into sections).
   - **Competitive MAS**: Agents might have conflicting objectives or constraints (e.g., in simulated games or negotiation tasks), where they must strategize to win or optimize their own outcome.

5. **Specialization**\
   Each agent may be specialized for a particular function. For instance, in an LLM context, one agent might be responsible for data retrieval (searching knowledge bases), another for code execution, and another for conversation with the user. Splitting tasks among specialized agents often makes the overall system more powerful.

6. **Emergent Behavior**\
   When multiple agents interact, new behaviors or solutions can emerge that weren’t explicitly programmed. In LLM-based multi-agent setups, you might see interesting chains of thought or unexpected creative solutions, especially if the agents can “critique” or “refine” each other’s outputs.

7. **Scalability**\
   One of the major benefits of multi-agent systems is that they can scale more easily than single-agent systems, especially if each agent can run in parallel or only spin up when needed. This lends itself well to distributed architectures in which each LLM agent can operate in a microservice-like environment.

8. **Challenges (Particularly with LLMs)**
   - **Coordination Overhead**: More agents can mean more communication overhead and potential confusion about who does what.
   - **Context/Memory Limits**: LLMs have token limits, so passing large amounts of context among multiple agents can get tricky.
   - **Safety & Security**: When agents can execute code, read/write files, or call external APIs, there must be strict access control and robust sandboxing.

9. **Frameworks & Patterns**
   - **Reactive vs. Deliberative Agents**: Reactive agents respond automatically to changes in the environment; deliberative agents plan ahead. Most LLM-based systems are somewhat deliberative (they reason step by step).
   - **ReAct Pattern**: A common design for LLM agents to handle reasoning and tool use, allowing them to “reflect” (i.e., reason) and “act” (i.e., call a tool).
   - **Workflow Orchestration**: Tools like Airflow, Prefect, or specialized “agent orchestration” libraries can coordinate the tasks of multiple LLMs.

In short, **multi-agent systems** provide a powerful paradigm for building AI solutions where multiple autonomous, specialized components can work together. In the realm of LLMs, it’s a way to scale beyond a single, monolithic prompt/response cycle—letting multiple “agentic” LLMs communicate, critique, and hand off tasks to reach solutions that a single LLM might struggle with on its own.

---

Now that we’ve set the stage on multi-agent systems, we can explore how to set up an *Agentic System* from **Level 1** (basic prompt + config) all the way to **Level 7** (dynamic workflow orchestration). Let’s begin whenever you’re ready.
