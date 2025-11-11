import grpc
# This import will show an error in PyCharm, but will run correctly
# if you ran the 'protoc' command locally at least once.
import notes_pb2
import notes_pb2_grpc


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = notes_pb2_grpc.NoteServiceStub(channel)

        print("--- Create Note ---")
        response = stub.CreateNote(notes_pb2.CreateNoteRequest(
            title="First Docker Note",
            content="This note is saved in SQLite inside Docker."
        ))
        note_id = response.id
        print(f"Created Note ID: {note_id}")

        print("\n--- Get Note ---")
        try:
            note_response = stub.GetNote(notes_pb2.GetNoteRequest(id=note_id))
            if note_response.note.id:
                print(f"Title: {note_response.note.title}, Content: {note_response.note.content}")
            else:
                print("Note not found (empty response).")

        except grpc.RpcError as e:
            print(f"Error: {e.details()}")

        print("\n--- List Notes ---")
        stub.CreateNote(notes_pb2.CreateNoteRequest(title="Meeting", content="10 AM with Team"))

        list_response = stub.ListNotes(notes_pb2.ListNotesRequest())
        for note in list_response.notes:
            print(f"- [{note.id}] {note.title}: {note.content}")

        print("\n--- Delete Note ---")
        del_response = stub.DeleteNote(notes_pb2.DeleteNoteRequest(id=note_id))
        print(f"Delete Status: {del_response.success}, Message: {del_response.message}")

        print("\n--- List Notes (After Delete) ---")
        list_response = stub.ListNotes(notes_pb2.ListNotesRequest())
        if not list_response.notes:
            print("No notes found.")
        for note in list_response.notes:
            print(f"- [{note.id}] {note.title}: {note.content}")


if __name__ == '__main__':
    run()