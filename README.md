# Note Management gRPC Service (with SQLite & Docker)

This project is a simple Note Management microservice built with gRPC, Python, SQLite, and containerized with Docker.

## Features

* **CreateNote**: Create a new note with a title and content.
* **GetNote**: Retrieve a note by its unique ID.
* **ListNotes**: Get a list of all notes in the database.
* **DeleteNote**: Remove a note by its unique ID.

## Tech Stack

* **gRPC**: Framework for high-performance RPC (Remote Procedure Call).
* **Protocol Buffers**: Language-neutral data serialization.
* **Python**: Programming language for the server and client.
* **SQLite**: Embedded SQL database for data persistence.
* **Docker**: Containerization platform for building and running the service.

---

## How to Run (Docker - Recommended)

This is the easiest way to get the server running.

**Prerequisites:**
* Docker and Docker Compose installed.

**Steps:**

1.  **Build and Run the Service:**
    Open your terminal in the project directory and run:
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker image (if it doesn't exist) and start the gRPC server. It will also create a `notes.db` file in your project directory.

2.  **Run the Client:**
    While the server is running (in the first terminal), open a **new terminal** and run the Python client:
    ```bash
    # (Optional: Create and activate a venv first)
    # python -m venv venv
    # source venv/bin/activate
    
    # Install client dependencies
    pip install grpcio grpcio-tools
    
    # Run the client
    python client.py
    ```
    The client will connect to `localhost:50051` (which Docker maps to the container) and test all the API endpoints.

---

## How to Run (Local Setup - Without Docker)

**Prerequisites:**
* Python 3.8+
* `pip` and `venv`

**Steps:**

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Generate gRPC Code:**
    (Note: The `server.py` file also attempts to do this, but it's good practice to do it manually first).
    ```bash
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. notes.proto
    ```
    This will create `notes_pb2.py` and `notes_pb2_grpc.py`.

4.  **Run the Server:**
    ```bash
    python server.py
    ```
    The server will start and create the `notes.db` file.

5.  **Run the Client:**
    Open a **new terminal** (and activate the `venv`):
    ```bash
    python client.py
    ```