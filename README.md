# 🚀 gRPC Note Management Service 📝

A simple, high-performance note management microservice built with **Python** and **gRPC**. It uses **SQLite** for persistence and is fully containerized with **Docker**.

This project serves as an excellent example of implementing a modern, high-performance client-server architecture using Protocol Buffers.

-----

## ✨ Key Features

  * **✅ CreateNote**: Create a new note with a title and content.
  * **✅ GetNote**: Retrieve a note by its unique ID.
  * **✅ DeleteNote**: Delete a note by its ID.
  * **✅ ListNotes**: Get a list of all notes currently in the database.

-----

## 🛠️ Tech Stack

  * **🔹 gRPC & Protocol Buffers**: For defining the service and handling high-speed, binary-based RPC communication.
  * **🐍 Python (3.10-slim)**: The core language for both the server and the client.
  * **🗃️ SQLite**: A lightweight, file-based database for persistent data storage.
  * **🐳 Docker & Docker Compose**: For building portable images and easily managing the service's runtime environment.

-----

## 📁 Project Structure

Understanding the file structure is key to understanding the project:

```
python-grpc-note-service/
│
├── 🐳 Dockerfile               # (Build Recipe) Instructions to build the Docker image
├── 🚢 docker-compose.yml       # (Run Command) Manages container runtime, ports, & volumes
│
├── 📜 notes.proto              # (The Contract) The heart of the project! Defines the gRPC service & messages
├── 🧠 server.py                # (The Brain) The gRPC server implementation & database logic
├── 👨‍🔬 client.py                 # (The Tester) A Python script to test the server
│
├── 🗃️ database.py             # (Storage Manager) A helper script to initialize the database table
├── 📦 requirements.txt        # (Shopping List) Required Python libraries
├── 🚫 .gitignore                # (The Filter) Ignores unnecessary files (like data, venv)
└── 📄 README.md                 # (The Manual) This file!
```

-----

## 🐳 How to Run (Docker - Recommended)

This is the simplest and fastest way to get the full service running.

### 1\. Prerequisites

  * **Docker** and **Docker Compose** must be installed on your system.

### 2\. Build & Run the Server

Open a terminal in the project's root directory and run the following command. This will build the Docker image, start the container, expose port `50051`, and create the `data` directory for the database.

```bash
docker-compose up --build
```

After running, you should see the server logs, indicating it's waiting for connections on port 50051:

```log
Attaching to grpc-server-1
grpc-server-1  | Database 'data/notes.db' initialized successfully.
grpc-server-1  | Server started on port 50051...
```

### 3\. Test with the Client

While the first terminal is running:

1.  Open a **new terminal**.
2.  (Optional but recommended) Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install the client dependencies (and gRPC tools):
    ```bash
    pip install grpcio grpcio-tools
    ```
4.  **(Important)** Generate the gRPC files locally so `client.py` can import them:
    ```bash
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. notes.proto
    ```
5.  Run the test client:
    ```bash
    python client.py
    ```

You should see the successful output from the test client, confirming it has communicated with the server running inside Docker\!

-----

## 💻 How to Run (Local Setup - No Docker)

This method is useful for developing and debugging `server.py` directly.

1.  **Create Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Generate gRPC Code:** (This is a crucial step)

    ```bash
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. notes.proto
    ```

    (This must create `notes_pb2.py` and `notes_pb2_grpc.py`)

4.  **Run the Server:** (In your first terminal)

    ```bash
    python server.py
    ```

    (The server will start and create the database file at `data/notes.db`)

5.  **Run the Client:** (In a second terminal)

    ```bash
    python client.py
    ```

-----

## 📜 API Contract (`notes.proto`)

This is the "menu" for our service, defining exactly what functions and data structures are available.

```protobuf
syntax = "proto3";

package notes;

// The Note service definition.
service NoteService {
  // Create a new note
  rpc CreateNote (CreateNoteRequest) returns (CreateNoteResponse);
  
  // Get a note by ID
  rpc GetNote (GetNoteRequest) returns (GetNoteResponse);
  
  // Delete a note by ID
  rpc DeleteNote (DeleteNoteRequest) returns (DeleteNoteResponse);
  
  // List all notes
  rpc ListNotes (ListNotesRequest) returns (ListNotesResponse);
}

// The Note message structure
message Note {
  string id = 1;
  string title = 2;
  string content = 3;
}

// Request message for CreateNote
message CreateNoteRequest {
  string title = 1;
  string content = 2;
}

// Response message for CreateNote
message CreateNoteResponse {
  string id = 1;
}

// Request message for GetNote
message GetNoteRequest {
  string id = 1;
}

// Response message for GetNote (wrapper)
message GetNoteResponse {
  Note note = 1;
}

// Request message for DeleteNote
message DeleteNoteRequest {
  string id = 1;
}

// Response message for DeleteNote
message DeleteNoteResponse {
  bool success = 1;
  string message = 2;
}

// Request message for ListNotes (empty)
message ListNotesRequest {}

// Response message for ListNotes
message ListNotesResponse {
  repeated Note notes = 1;
}
```
