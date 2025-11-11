import grpc
from concurrent import futures
import uuid
import sqlite3
import database  # Import our database initializer

# These imports will fail in PyCharm but work in Docker
import notes_pb2
import notes_pb2_grpc

DB_NAME = database.DB_NAME  # Use the path from database.py


class NoteService(notes_pb2_grpc.NoteServiceServicer):

    def get_db_connection(self):
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    def CreateNote(self, request, context):
        note_id = str(uuid.uuid4())
        try:
            with self.get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO notes (id, title, content) VALUES (?, ?, ?)",
                    (note_id, request.title, request.content)
                )
                conn.commit()
            print(f"Note created with ID: {note_id}")
            # --- CORRECTED ---
            # Return only the string ID
            return notes_pb2.CreateNoteResponse(id=note_id)
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {e}")
            return notes_pb2.CreateNoteResponse()

    def GetNote(self, request, context):
        with self.get_db_connection() as conn:
            cursor = conn.execute("SELECT id, title, content FROM notes WHERE id = ?", (request.id,))
            row = cursor.fetchone()

        if row:
            # Convert row to Note message
            note_message = notes_pb2.Note(id=row['id'], title=row['title'], content=row['content'])
            # --- CORRECTED ---
            # Wrap the Note inside a GetNoteResponse
            return notes_pb2.GetNoteResponse(note=note_message)
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Note not found')
            # Return an empty GetNoteResponse
            return notes_pb2.GetNoteResponse()

    def DeleteNote(self, request, context):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute("SELECT 1 FROM notes WHERE id = ?", (request.id,))
                if cursor.fetchone() is None:
                    return notes_pb2.DeleteNoteResponse(success=False, message="Note ID not found")
                conn.execute("DELETE FROM notes WHERE id = ?", (request.id,))
                conn.commit()
            return notes_pb2.DeleteNoteResponse(success=True, message="Deleted successfully")
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {e}")
            return notes_pb2.DeleteNoteResponse(success=False, message=str(e))

    def ListNotes(self, request, context):
        all_notes = []
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute("SELECT id, title, content FROM notes")
                rows = cursor.fetchall()
                for row in rows:
                    all_notes.append(notes_pb2.Note(id=row['id'], title=row['title'], content=row['content']))
            return notes_pb2.ListNotesResponse(notes=all_notes)
        except sqlite3.Error as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Database error: {e}")
            return notes_pb2.ListNotesResponse()


def serve():
    # Initialize the database
    database.init_db()

    # --- PROTOC SECTION REMOVED ---
    # The build is now done in the Dockerfile

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    notes_pb2_grpc.add_NoteServiceServicer_to_server(NoteService(), server)

    server.add_insecure_port('[::]:50051')
    print("Server started on port 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()