## Low-Level Design (LLD)

This LLD provides detailed specifications for the modules, database, APIs, UI/UX, and other critical aspects of the AI Agent & Workflow Management Platform.

---

### I. Module-Specific Design

#### 1. User & Auth Service

* **Responsibilities:** User registration, login, profile management, JWT generation and validation, role-based access control management.
* **Database Schema (`users`, `roles`, `user_roles`):**
    * `users` (user_id (PK, UUID), username (VARCHAR, UNIQUE), email (VARCHAR, UNIQUE), password_hash (VARCHAR), first_name (VARCHAR), last_name (VARCHAR), created_at (TIMESTAMP), updated_at (TIMESTAMP))
    * `roles` (role_id (PK, SERIAL), role_name (VARCHAR, UNIQUE)) - e.g., 'user', 'admin'
    * `user_roles` (user_id (FK), role_id (FK), PRIMARY KEY (user_id, role_id))
* **API Endpoints:**
    * `POST /auth/register`
    * `POST /auth/login`
    * `POST /auth/refresh-token`
    * `GET /users/me`
    * `PUT /users/me`
    * (Admin endpoints for user management if needed: `GET /users`, `PUT /users/{id}/role`)

#### 2. Agent Service

* **Responsibilities:** CRUD operations for agent definitions.
* **Database Schema (`agents`, `agent_knowledge_bases`):**
    * `agents` (agent_id (PK, UUID), user_id (FK to `users.user_id`), name (VARCHAR), role (TEXT), goal (TEXT), backstory (TEXT), llm_model_id (FK to `llm_models.model_id`), tools_config (JSONB, stores array of tool definitions e.g., `[{"name": "search_tool", "type": "duckduckgo", "config": {}}]`), verbose_flag (BOOLEAN DEFAULT FALSE), memory_flag (BOOLEAN DEFAULT FALSE), max_iter (INTEGER DEFAULT 15), max_rpm (INTEGER, NULLABLE), created_at (TIMESTAMP), updated_at (TIMESTAMP))
    * `agent_knowledge_bases` (agent_kb_id (PK, UUID), agent_id (FK to `agents.agent_id`), kb_id (FK to `knowledge_bases.kb_id`)) - Junction table
* **API Endpoints:**
    * `POST /agents`
    * `GET /agents` (with pagination, filtering by user)
    * `GET /agents/{agent_id}`
    * `PUT /agents/{agent_id}`
    * `DELETE /agents/{agent_id}`
* **Logic for crewAI Agent objects:** The service will primarily store the *configuration* for agents. The `crewAI Orchestration Engine` will use this configuration to instantiate `crewAI.Agent` objects dynamically during workflow execution. This includes fetching the LLM configuration from the `Model Management Service` using `llm_model_id`. Tools will be a JSON array defining tool names and any necessary simple configurations; complex tool objects/functions will be mapped/instantiated in the Orchestration Engine.

#### 3. Workflow (Crew) Service

* **Responsibilities:** CRUD for workflows and their associated tasks.
* **Database Schema (`workflows`, `workflow_agents`, `tasks`):**
    * `workflows` (workflow_id (PK, UUID), user_id (FK to `users.user_id`), name (VARCHAR), description (TEXT), process_type (VARCHAR - 'sequential', 'hierarchical'), created_at (TIMESTAMP), updated_at (TIMESTAMP))
    * `workflow_agents` (workflow_agent_id (PK, UUID), workflow_id (FK to `workflows.workflow_id`), agent_id (FK to `agents.agent_id`), alias_in_workflow (VARCHAR, optional, for user-friendly naming within the workflow context), sequence_order (INTEGER, for UI ordering or simple sequential setup))
    * `tasks` (task_id (PK, UUID), workflow_id (FK to `workflows.workflow_id`), assigned_workflow_agent_id (FK to `workflow_agents.workflow_agent_id`), description (TEXT), expected_output (TEXT), context_task_ids (JSONB, array of `task_id`s this task depends on), human_input_required (BOOLEAN DEFAULT FALSE), config_json (JSONB, e.g., specific tools for this task, parameters), created_at (TIMESTAMP), updated_at (TIMESTAMP))
* **API Endpoints:**
    * `POST /workflows`
    * `GET /workflows` (with pagination, filtering)
    * `GET /workflows/{workflow_id}`
    * `PUT /workflows/{workflow_id}` (for workflow metadata)
    * `DELETE /workflows/{workflow_id}`
    * `POST /workflows/{workflow_id}/execute` (triggers execution via Task Queue)
    * `GET /workflows/{workflow_id}/status` (fetches latest execution status)
    * `POST /workflows/{workflow_id}/tasks` (to add a task to a workflow)
    * `GET /workflows/{workflow_id}/tasks` (to list tasks for a workflow)
    * `PUT /tasks/{task_id}` (to update a task)
    * `DELETE /tasks/{task_id}` (to remove a task from a workflow)
* **Logic for UI to crewAI:**
    * **Drag-and-Drop:** Frontend sends a structured JSON representing the workflow graph (nodes are agents, edges define task sequence/dependencies, and task properties).
    * **Translation:**
        1.  Workflow Service creates/updates `workflows` record.
        2.  For each agent on the canvas assigned to the workflow, it creates/updates a `workflow_agents` record, linking the generic `agent_id` to this specific workflow instance.
        3.  For each task defined:
            * A `tasks` record is created.
            * `assigned_workflow_agent_id` links to the specific agent instance in the `workflow_agents` table.
            * `context_task_ids` stores dependencies between tasks, derived from UI connections.
    * **Sequence Diagrams:**
        * **Workflow Creation:**
            ```mermaid
            sequenceDiagram
                participant User
                participant Frontend
                participant APIGateway as API Gateway
                participant WorkflowService as WS
                participant Database as DB

                User->>Frontend: Designs workflow, adds agents, defines tasks
                Frontend->>APIGateway: POST /api/workflows (workflow_data_json)
                APIGateway->>WS: Validate & forward request
                WS->>DB: Create Workflow record
                WS->>DB: Create WorkflowAgent records for each agent in workflow
                WS->>DB: Create Task records with descriptions, agent assignments, dependencies
                DB-->>WS: Confirmations
                WS-->>APIGateway: Success response (workflow_id)
                APIGateway-->>Frontend: Success response
                Frontend-->>User: Workflow saved
            ```
        * **Workflow Execution:**
            ```mermaid
            sequenceDiagram
                participant User
                participant Frontend
                participant APIGateway as API Gateway
                participant WorkflowService as WS
                participant TaskQueue as TQ
                participant CrewAIOrchestrationEngine as COE
                participant AgentService as AS
                participant ModelManagementService as MMS
                participant KnowledgeBaseService as KBS
                participant ExecutionMonitoringService as EMS
                participant CrewAILib as crewAI
                participant ExternalLLMs

                User->>Frontend: Clicks "Execute" on a workflow
                Frontend->>APIGateway: POST /api/workflows/{id}/execute
                APIGateway->>WS: Validate & forward request
                WS->>DB: Fetch workflow, agents, tasks definitions
                WS->>TQ: Enqueue execution task (workflow_id, user_id, parameters)
                TQ-->>WS: Task accepted
                WS-->>APIGateway: Execution initiated (async)
                APIGateway-->>Frontend: Execution started
                Frontend-->>User: Workflow is running (UI shows pending/running)

                COE->>TQ: Dequeue execution task
                COE->>EMS: Log execution start (new execution_id)
                COE->>AS: Fetch agent details (role, goal, etc.) for all agents in workflow
                AS-->>COE: Agent definitions
                COE->>MMS: Fetch LLM configurations for agents
                MMS-->>COE: LLM configs
                COE->>KBS: (If RAG tool needed) Fetch KB access details/tool config
                KBS-->>COE: KB tool info
                COE->>crewAI: Instantiate Agents (with LLMs, tools)
                COE->>crewAI: Instantiate Tasks (with descriptions, assigned agents, context)
                COE->>crewAI: Instantiate Crew (with agents, tasks, process)
                COE->>crewAI: crew.kickoff()
                loop For each step/task in crewAI execution
                    crewAI->>ExternalLLMs: LLM API Calls
                    ExternalLLMs-->>crewAI: LLM Responses
                    crewAI-->>COE: Progress, intermediate outputs, logs
                    COE->>EMS: Log step details, agent outputs, tokens used (if available)
                end
                crewAI-->>COE: Final output / Error
                COE->>EMS: Log final output, status (completed/failed), duration
            ```

#### 4. Model Management Service

* **Responsibilities:** CRUD for LLM model configurations.
* **Database Schema (`llm_models`):**
    * `llm_models` (model_id (PK, UUID), user_id (FK to `users.user_id`, NULLABLE if admin-managed global models), name (VARCHAR), provider (VARCHAR - e.g., 'OpenAI', 'Anthropic', 'Ollama', 'AzureOpenAI', 'GoogleVertexAI'), model_identifier (VARCHAR - e.g., 'gpt-4o', 'claude-3-opus', 'llama3:latest'), api_key_encrypted (VARCHAR, NULLABLE), endpoint_url (VARCHAR, NULLABLE - for Ollama or custom APIs), config_params_json (JSONB - e.g., `{"temperature": 0.7, "max_tokens": 2000}`), created_at (TIMESTAMP), updated_at (TIMESTAMP))
* **API Endpoints:**
    * `POST /models`
    * `GET /models` (list available models, filter by user or global)
    * `GET /models/{model_id}`
    * `PUT /models/{model_id}`
    * `DELETE /models/{model_id}`

#### 5. Knowledge Base Service

* **Responsibilities:** Manage knowledge base creation, document ingestion, processing, indexing, and retrieval.
* **Database Schema (`knowledge_bases`, `kb_documents`):**
    * `knowledge_bases` (kb_id (PK, UUID), user_id (FK to `users.user_id`), name (VARCHAR), description (TEXT), source_type (VARCHAR - e.g., 'upload', 'web_url', 'direct_text'), status (VARCHAR - 'pending', 'indexing', 'ready', 'error'), vector_db_collection_name (VARCHAR, unique), created_at (TIMESTAMP), updated_at (TIMESTAMP))
    * `kb_documents` (document_id (PK, UUID), kb_id (FK to `knowledge_bases.kb_id`), original_file_name (VARCHAR, NULLABLE), storage_path_or_url (VARCHAR, NULLABLE), content_hash (VARCHAR, NULLABLE), status (VARCHAR - 'pending_processing', 'processing', 'processed', 'error_processing'), num_chunks (INTEGER), processed_at (TIMESTAMP), created_at (TIMESTAMP))
* **Process for Document Ingestion:**
    1.  **Upload/Link:** User provides document(s)/URL/text via API (`POST /knowledge-bases/{kb_id}/documents` or `POST /knowledge-bases/{kb_id}/text-content`).
    2.  **Storage:** If file, Knowledge Base Service saves it to Object Storage and records path in `kb_documents`.
    3.  **Queueing:** A task is added to the Task Queue (Celery) with `document_id` and `kb_id`.
    4.  **Worker Processing:**
        * A dedicated worker (part of KB Service) picks up the task.
        * Loads document content (using LangChain or similar loaders).
        * Cleans and chunks the text (e.g., RecursiveCharacterTextSplitter).
        * Generates embeddings for each chunk using a selected embedding model (this model could be managed via `Model Management Service` or be a fixed choice).
        * Stores chunks (text + embedding) in the Vector Database (e.g., ChromaDB, in a collection named after `kb_id` or a unique identifier stored in `knowledge_bases.vector_db_collection_name`).
        * Updates `kb_documents.status` to 'processed' and `knowledge_bases.status` to 'ready' (if all docs processed).
* **Mechanism for RAG with crewAI Agents:**
    * **Custom Tool:** A custom crewAI `Tool` will be dynamically created by the `crewAI Orchestration Engine` if an agent is associated with one or more KBs.
    * **Tool Name:** E.g., `knowledge_base_search_tool`.
    * **Tool Description:** "Searches the assigned knowledge base(s) to answer questions or find relevant information based on the input query."
    * **Tool Logic (`_run` method):**
        1.  Takes a search query string as input.
        2.  Makes an API call to the Knowledge Base Service: `POST /knowledge-bases/query` (body: `{"kb_ids": ["id1", "id2"], "query": "user query", "top_k": 3}`).
        3.  The KB Service endpoint queries the Vector Database for the specified `kb_ids` using the input query.
        4.  Returns the retrieved context (concatenated relevant chunks) as a string.
    * This tool is then added to the `tools` list of the crewAI `Agent` instance.

#### 6. crewAI Orchestration Engine

* **Responsibilities:** Dynamically construct and execute crewAI crews. This is not a user-facing API service but a backend worker.
* **Interaction with crewAI Library:**
    1.  **Receive Task:** Gets workflow execution details from the Task Queue.
    2.  **Fetch Data:** Retrieves full configurations for agents, LLMs (from Model Mgmt Service), and KB associations (from Agent Service & KB Service) using their respective IDs.
    3.  **Instantiate Agents:** For each agent in the workflow:
        * `llm = ...` (instantiate LLM object based on model config, e.g., `ChatOpenAI(api_key=..., model_name=...)`).
        * `tools = []` (instantiate standard crewAI tools or custom tools, like the RAG tool described above).
        * `agent = Agent(role=..., goal=..., backstory=..., llm=llm, tools=tools, verbose=..., memory=..., max_iter=..., max_rpm=...)`.
    4.  **Instantiate Tasks:** For each task in the workflow:
        * `agent_for_task = ...` (select the correct instantiated agent object).
        * `context_tasks_objects = [...]` (map `context_task_ids` to actual instantiated task objects if needed for `context` param).
        * `task = Task(description=..., expected_output=..., agent=agent_for_task, context=context_tasks_objects, human_input=...)`.
    5.  **Instantiate Crew:**
        * `crew_agents = [...]` (list of instantiated agent objects).
        * `crew_tasks = [...]` (list of instantiated task objects).
        * `process = Process.sequential` or `Process.hierarchical` based on `workflows.process_type`.
        * `crew = Crew(agents=crew_agents, tasks=crew_tasks, process=process, verbose=..., memory=..., manager_llm=... (if hierarchical))`.
    6.  **Execute:** `result = crew.kickoff(inputs=...)`. The initial `inputs` might come from the workflow execution trigger or be predefined.
    7.  **Capture Output & Logs:**
        * Capture `crew.usage_metrics` (token counts, etc.).
        * Structure the `result` and any intermediate logs/errors.
        * Send this data to the `Execution & Monitoring Service`.
* **Management of Concurrent Workflow Executions:** Celery workers will handle concurrency. Each worker processes one workflow execution at a time. The number of concurrent workers can be scaled based on load. Ensure sufficient resources (CPU, memory) for each worker.

#### 7. Execution & Monitoring Service

* **Responsibilities:** Storing and retrieving detailed logs and outputs of workflow executions.
* **Database Schema (`workflow_executions`, `task_executions`):**
    * `workflow_executions` (execution_id (PK, UUID), workflow_id (FK to `workflows.workflow_id`), user_id (FK to `users.user_id`), start_time (TIMESTAMP), end_time (TIMESTAMP, NULLABLE), duration_ms (INTEGER, NULLABLE), status (VARCHAR - 'pending', 'running', 'completed', 'failed', 'cancelled'), inputs_json (JSONB, initial inputs to the workflow), final_output_json (JSONB, NULLABLE, final result of the crew), usage_metrics_json (JSONB, NULLABLE, e.g., token counts), created_at (TIMESTAMP))
    * `task_executions` (task_execution_id (PK, UUID), execution_id (FK to `workflow_executions.execution_id`), task_id (FK to `tasks.task_id`), assigned_agent_id (FK to `agents.agent_id`), start_time (TIMESTAMP), end_time (TIMESTAMP, NULLABLE), duration_ms (INTEGER, NULLABLE), status (VARCHAR - 'pending', 'running', 'completed', 'failed'), inputs_data (JSONB, NULLABLE, input to the task), output_data (TEXT or JSONB, NULLABLE, output of the task agent), logs_text (TEXT, NULLABLE, detailed logs from agent execution), error_message (TEXT, NULLABLE), created_at (TIMESTAMP))
* **API Endpoints (primarily for internal use by COE and for frontend to fetch status/results):**
    * `POST /executions` (internal, called by COE to create execution records)
    * `PUT /executions/{execution_id}` (internal, called by COE to update status, end_time, output)
    * `GET /executions/{execution_id}` (for frontend to get detailed status and results)
    * `GET /workflows/{workflow_id}/executions` (list all executions for a workflow)
    * `GET /executions/{execution_id}/tasks` (list task execution details for a workflow execution)

#### 8. Analytics Service

* **Responsibilities:** Aggregating execution data for KPIs.
* **Logic for Aggregating Data:**
    * SQL queries against `workflow_executions`, `task_executions`, `agents`, `workflows` tables.
    * E.g., `SELECT COUNT(*) FROM agents WHERE user_id = :user_id;`
    * E.g., `SELECT status, COUNT(*) FROM workflow_executions GROUP BY status;`
    * E.g., `SELECT AVG(duration_ms) FROM workflow_executions WHERE status = 'completed';`
* **API Endpoints:**
    * `GET /analytics/summary` (overall counts, success/failure rates)
    * `GET /analytics/workflow-performance` (avg execution times, etc.)
    * `GET /analytics/resource-usage` (frequently used agents/models - requires joining with `agents` and `llm_models` through execution data)
* **Conceptual Dashboard UI Elements:**
    * **Summary Cards:** "Total Agents", "Total Workflows", "Workflows Executed (24h)", "Success Rate".
    * **Charts:**
        * "Workflow Executions Over Time" (Line/Bar chart: count of executions per day/week).
        * "Execution Status Distribution" (Pie chart: completed, failed, running).
        * "Average Workflow Duration" (Line chart over time).
        * "Top 5 Most Used Agents" (Bar chart).
        * "Top 5 Most Used LLM Models" (Bar chart).
    * **Tables:** "Recent Workflow Executions" (with status, duration, link to details).

---

### II. Database Design (Consolidated)

* **Choice Justification:** PostgreSQL is chosen for its robust relational capabilities, ACID compliance, excellent JSONB support (for flexible fields like `tools_config`, `config_params_json`), and scalability options. The Vector Database (ChromaDB) is separate but linked logically via IDs.

* **Schema Overview (Primary & Foreign Keys indicated):**

    * **`users`**
        * `user_id` (PK, UUID)
        * `username` (VARCHAR, UNIQUE)
        * `email` (VARCHAR, UNIQUE)
        * `password_hash` (VARCHAR)
        * `created_at` (TIMESTAMP)
        * `updated_at` (TIMESTAMP)

    * **`roles`**
        * `role_id` (PK, SERIAL)
        * `role_name` (VARCHAR, UNIQUE)

    * **`user_roles`**
        * `user_id` (FK to `users.user_id`)
        * `role_id` (FK to `roles.role_id`)
        * PRIMARY KEY (`user_id`, `role_id`)

    * **`llm_models`**
        * `model_id` (PK, UUID)
        * `user_id` (FK to `users.user_id`, NULLABLE)
        * `name` (VARCHAR)
        * `provider` (VARCHAR)
        * `model_identifier` (VARCHAR)
        * `api_key_encrypted` (VARCHAR, NULLABLE)
        * `endpoint_url` (VARCHAR, NULLABLE)
        * `config_params_json` (JSONB)
        * `created_at` (TIMESTAMP)
        * `updated_at` (TIMESTAMP)

    * **`agents`**
        * `agent_id` (PK, UUID)
        * `user_id` (FK to `users.user_id`)
        * `name` (VARCHAR)
        * `role` (TEXT)
        * `goal` (TEXT)
        * `backstory` (TEXT)
        * `llm_model_id` (FK to `llm_models.model_id`)
        * `tools_config` (JSONB)
        * `verbose_flag` (BOOLEAN)
        * `memory_flag` (BOOLEAN)
        * `max_iter` (INTEGER)
        * `max_rpm` (INTEGER, NULLABLE)
        * `created_at` (TIMESTAMP)
        * `updated_at` (TIMESTAMP)

    * **`knowledge_bases`**
        * `kb_id` (PK, UUID)
        * `user_id` (FK to `users.user_id`)
        * `name` (VARCHAR)
        * `description` (TEXT)
        * `source_type` (VARCHAR)
        * `status` (VARCHAR)
        * `vector_db_collection_name` (VARCHAR, UNIQUE)
        * `created_at` (TIMESTAMP)
        * `updated_at` (TIMESTAMP)

    * **`kb_documents`**
        * `document_id` (PK, UUID)
        * `kb_id` (FK to `knowledge_bases.kb_id`)
        * `original_file_name` (VARCHAR, NULLABLE)
        * `storage_path_or_url` (VARCHAR, NULLABLE)
        * `content_hash` (VARCHAR, NULLABLE)
        * `status` (VARCHAR)
        * `num_chunks` (INTEGER)
        * `processed_at` (TIMESTAMP, NULLABLE)
        * `created_at` (TIMESTAMP)

    * **`agent_knowledge_bases`** (Junction Table)
        * `agent_kb_id` (PK, UUID)
        * `agent_id` (FK to `agents.agent_id`)
        * `kb_id` (FK to `knowledge_bases.kb_id`)
        * UNIQUE (`agent_id`, `kb_id`)

    * **`workflows`**
        * `workflow_id` (PK, UUID)
        * `user_id` (FK to `users.user_id`)
        * `name` (VARCHAR)
        * `description` (TEXT)
        * `process_type` (VARCHAR)
        * `created_at` (TIMESTAMP)
        * `updated_at` (TIMESTAMP)

    * **`workflow_agents`** (Agent instance within a workflow)
        * `workflow_agent_id` (PK, UUID)
        * `workflow_id` (FK to `workflows.workflow_id`)
        * `agent_id` (FK to `agents.agent_id`)
        * `alias_in_workflow` (VARCHAR, NULLABLE)
        * `sequence_order` (INTEGER, NULLABLE)

    * **`tasks`**
        * `task_id` (PK, UUID)
        * `workflow_id` (FK to `workflows.workflow_id`)
        * `assigned_workflow_agent_id` (FK to `workflow_agents.workflow_agent_id`)
        * `description` (TEXT)
        * `expected_output` (TEXT)
        * `context_task_ids` (JSONB ARRAY of `tasks.task_id`)
        * `human_input_required` (BOOLEAN)
        * `config_json` (JSONB, e.g., tool overrides)
        * `created_at` (TIMESTAMP)
        * `updated_at` (TIMESTAMP)

    * **`workflow_executions`**
        * `execution_id` (PK, UUID)
        * `workflow_id` (FK to `workflows.workflow_id`)
        * `user_id` (FK to `users.user_id`)
        * `start_time` (TIMESTAMP)
        * `end_time` (TIMESTAMP, NULLABLE)
        * `duration_ms` (INTEGER, NULLABLE)
        * `status` (VARCHAR)
        * `inputs_json` (JSONB)
        * `final_output_json` (JSONB, NULLABLE)
        * `usage_metrics_json` (JSONB, NULLABLE)
        * `created_at` (TIMESTAMP)

    * **`task_executions`**
        * `task_execution_id` (PK, UUID)
        * `execution_id` (FK to `workflow_executions.execution_id`)
        * `task_id` (FK to `tasks.task_id`) // Original task definition
        * `assigned_agent_id` (FK to `agents.agent_id`) // Actual agent that ran
        * `start_time` (TIMESTAMP)
        * `end_time` (TIMESTAMP, NULLABLE)
        * `duration_ms` (INTEGER, NULLABLE)
        * `status` (VARCHAR)
        * `inputs_data` (JSONB, NULLABLE)
        * `output_data` (TEXT or JSONB, NULLABLE)
        * `logs_text` (TEXT, NULLABLE)
        * `error_message` (TEXT, NULLABLE)
        * `created_at` (TIMESTAMP)

---

### III. API Specifications (Example Detail Level)

All endpoints will require `Authorization: Bearer <JWT_TOKEN>` header unless specified (e.g., login/register).
Standard success responses: 200 OK, 201 Created, 204 No Content.
Standard error responses: 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Server Error.
Error Response Body Schema: `{"detail": "Error message string", "error_code": "OPTIONAL_UNIQUE_ERROR_CODE"}`

**Example: Agent Service API - `POST /agents`**

* **HTTP Method:** `POST`
* **URL Path:** `/api/v1/agents`
* **Request Headers:**
    * `Authorization: Bearer <JWT_TOKEN>`
    * `Content-Type: application/json`
* **Request Body (JSON Schema):**
    ```json
    {
      "type": "object",
      "properties": {
        "name": { "type": "string", "minLength": 1, "maxLength": 255 },
        "role": { "type": "string", "minLength": 1 },
        "goal": { "type": "string", "minLength": 1 },
        "backstory": { "type": "string" },
        "llm_model_id": { "type": "string", "format": "uuid" },
        "tools_config": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "type": { "type": "string" },
              "config": { "type": "object" }
            },
            "required": ["name", "type"]
          }
        },
        "verbose_flag": { "type": "boolean", "default": false },
        "memory_flag": { "type": "boolean", "default": false },
        "max_iter": { "type": "integer", "minimum": 1, "default": 15 },
        "max_rpm": { "type": "integer", "minimum": 0, "nullable": true },
        "associated_kb_ids": {
          "type": "array",
          "items": { "type": "string", "format": "uuid" },
          "nullable": true
        }
      },
      "required": ["name", "role", "goal", "backstory", "llm_model_id"]
    }
    ```
* **Response Body (201 Created - JSON Schema):**
    ```json
    {
      "type": "object",
      "properties": {
        "agent_id": { "type": "string", "format": "uuid" },
        "user_id": { "type": "string", "format": "uuid" },
        "name": { "type": "string" },
        "role": { "type": "string" },
        "goal": { "type": "string" },
        "backstory": { "type": "string" },
        "llm_model_id": { "type": "string", "format": "uuid" },
        "tools_config": { "type": "array", "items": { "type": "object" } },
        "verbose_flag": { "type": "boolean" },
        "memory_flag": { "type": "boolean" },
        "max_iter": { "type": "integer" },
        "max_rpm": { "type": "integer", "nullable": true },
        "created_at": { "type": "string", "format": "date-time" },
        "updated_at": { "type": "string", "format": "date-time" },
        "knowledge_bases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kb_id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"}
                }
            }
        }
      }
    }
    ```
* **Status Codes:**
    * `201 Created`: Agent created successfully.
    * `400 Bad Request`: Invalid input data (validation error).
    * `401 Unauthorized`: Missing or invalid JWT.
    * `404 Not Found`: `llm_model_id` or `kb_id` does not exist.
    * `422 Unprocessable Entity`: Semantic error not caught by schema validation.

*(Detailed specifications for all other CRUD endpoints for agents, workflows, tasks, models, KBs, and execution/analytics endpoints would follow a similar pattern, outlining method, path, headers, request/response schemas, and status codes.)*

---

### IV. User Interface (UI) & User Experience (UX) Considerations

Emphasis on an intuitive, guided user experience.

* **Agent Creation/Editing Form:**
    * Clear labels, input fields for name, role, goal, backstory.
    * Dropdown (searchable) for selecting an LLM Model (from `ModelManagementService`).
    * Tool Management:
        * Option 1: Predefined list of common crewAI tools (Search, Scraper, etc.) with checkboxes.
        * Option 2: A dynamic list where users can add "custom tools" by specifying a name and perhaps some simple parameters.
    * Toggles for "Verbose Mode" and "Memory".
    * Number inputs for "Max Iterations" and "Max RPM" (with sensible defaults and info tooltips).
    * Multi-select dropdown (searchable) for associating Knowledge Bases.
    * "Save Agent" / "Update Agent" buttons.
* **Workflow Design Canvas (e.g., using React Flow or similar):**
    * **Left Panel (Agent Pool):** List of created agents, draggable onto the canvas.
    * **Center Canvas:** Drop agents here. Agents appear as nodes.
    * **Connections:** Users draw connections between agent nodes to define task flow/dependencies.
    * **Right Panel (Properties Inspector):**
        * When canvas is selected: Workflow Name, Description, Process Type (Dropdown: Sequential, Hierarchical).
        * When an agent node is selected: Shows agent details (read-only).
        * When a connection/task is selected: Opens Task Definition Modal.
    * "Save Workflow" / "Execute Workflow" buttons.
* **Task Definition Modal (pops up when linking agents or clicking a task):**
    * **Task For Agent:** [Agent Name] (derived from the target agent node).
    * **Task Description:** Textarea.
    * **Expected Output:** Textarea.
    * **Context (Dependencies):** Auto-populated or manually selectable.
    * **Human Input Required:** Checkbox.
    * "Save Task" / "Update Task" buttons.
* **Knowledge Base Creation/Management Page:**
    * "Create New KB" button. Form: Name, Description.
    * Table of KBs: Name, Status, # Docs, Created Date, Actions (Manage Documents, Re-index, Edit, Delete).
    * **KB Detail/Document Management View:**
        * Upload area (drag & drop) / Add URL input / Add Text input.
        * List of documents: Name, Status, Actions.
* **Model Management Page:**
    * "Add New LLM" button. Form: Name, Provider, Model Identifier, API Key, Endpoint, `config_params`.
    * Table of LLMs: Name, Provider, Model ID, Actions.
* **Analytics Dashboard:** As described in LLD Section I.8. Interactive charts, date range selectors.
* **Workflow Execution Status Page:**
    * Real-time updates (WebSockets or polling).
    * Overall status: Workflow Name, Status, Start/End Time, Duration.
    * Visual representation of tasks. Each task shows: Agent, Status, Duration. Expandable section for logs, output.
    * Option to "Cancel" a running workflow.
* **Key User Interaction Flows:**
    * Guided Creation: Wizards for first agent/workflow.
    * Cloning: Allow cloning of agents and workflows.
    * Feedback: Clear success/error messages, loading indicators.

---

### V. Error Handling and Logging

* **System-Wide Error Handling Strategy:**
    * **API Level:** Consistent JSON error responses.
    * **User-Facing:** Frontend translates API errors into user-friendly notifications.
    * **Service Level:** Internal errors logged comprehensively. Retries with exponential backoff for transient errors. Circuit breaker pattern.
* **Detailed Logging Plan:**
    * **Log Format:** Structured logging (JSON). Include `timestamp`, `level`, `service_name`, `correlation_id`, `user_id`, `message`, `stack_trace`.
    * **Log Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL.
    * **What to Log:**
        * **API Gateway:** Incoming requests, response status, latency.
        * **All Services:** Startup/shutdown, key business logic operations, external API calls, errors, security events.
        * **crewAI Orchestration Engine:** Detailed logs from crewAI execution (iterations, tool usage, thoughts, LLM prompts, outputs).
    * **Log Storage & Analysis:** Centralized logging solution (e.g., ELK Stack, Grafana Loki).
    * **Correlation IDs:** Generate at API Gateway, pass through all services, log with every message.

---

### VI. Security Details

* **Authentication Mechanism:**
    * **JWT (JSON Web Tokens):**
        * Login -> Issues short-lived access token & longer-lived refresh token.
        * Access token in `Authorization: Bearer <token>` header.
        * Refresh token (HttpOnly cookie) to get new access token.
* **Authorization Rules (Role-Based Access Control - RBAC):**
    * **Roles:** `user`, `admin`.
    * **Permissions:** Defined per role for CRUD operations on own/all resources.
    * Implementation: Middleware validates JWT, extracts roles, checks permissions.
* **Data Encryption:**
    * **In Transit:** TLS 1.2/1.3 (HTTPS).
    * **At Rest:**
        * Encrypt LLM API keys using symmetric encryption (AES-256) with keys from a secrets manager.
        * Consider PostgreSQL TDE or column-level encryption for other sensitive PII.
        * Server-side encryption for documents in Object Storage.
* **Other Security Considerations:**
    * **Input Validation:** Pydantic models for request validation. Sanitize outputs (XSS).
    * **SQL Injection Prevention:** Use ORMs.
    * **Secrets Management:** HashiCorp Vault, Kubernetes Secrets, or cloud provider's manager.
    * **Rate Limiting:** On API Gateway.
    * **Helmet/Security Headers:** Middleware for HTTP security headers.
    * **Dependency Scanning:** Regular scans for vulnerabilities.
    * **Least Privilege.**
    * **Regular Security Audits & Penetration Testing.**
