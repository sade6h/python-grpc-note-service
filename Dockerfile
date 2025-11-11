# Use an official Python runtime as a parent image
# Using 3.10-slim as it's very stable
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code
# --- CORRECTED ---
COPY . .

# Run the gRPC code generator to create pb2 and pb2_grpc files
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. notes.proto

# Make port 50051 available
EXPOSE 50051

# Run server.py when the container launches
CMD ["python", "server.py"]