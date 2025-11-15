import grpc
import notes_pb2
import notes_pb2_grpc


def run():
    # Connect to the gRPC server (running in Docker)
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = notes_pb2_grpc.NoteServiceStub(channel)

        print("gRPC Note Client Started. Connecting to server...")

        # --- 1. Create Notes (Looping with y/n) ---
        print("\n--- 1. Create Notes ---")

        # --- تغییر یافته ---
        # ما اکنون یک لیست از تاپل‌ها (id, title) را ذخیره می‌کنیم
        created_notes_info = []
        note_counter = 1

        while True:
            print(f"\nCreating Note #{note_counter}...")
            # 1. Get input from the user
            user_title = input("  Enter note title: ")
            user_content = input("  Enter note content: ")

            request_message = notes_pb2.CreateNoteRequest(
                title=user_title,
                content=user_content
            )

            try:
                response = stub.CreateNote(request_message)
                print(f"✅ Success! Note created with ID: {response.id}")

                # --- تغییر یافته ---
                # هم ID و هم Title را ذخیره می‌کنیم
                created_notes_info.append((response.id, user_title))
                note_counter += 1

            except grpc.RpcError as e:
                print(f"❌ Error creating note: {e.details()}")

            # 4. سوال برای ادامه دادن
            continue_choice = ''
            while continue_choice not in ('y', 'n'):
                continue_choice = input("Do you want to create another note? (y/n): ").strip().lower()
                if continue_choice not in ('y', 'n'):
                    print("Invalid input. Please enter 'y' or 'n'.")

            if continue_choice == 'n':
                break

        # --- 2. Get Note (Based on user ID prompt) ---
        print("\n--- 2. Get a Specific Note ---")

        # --- تغییر یافته ---
        if not created_notes_info:
            print("No notes were created, skipping 'Get Note'.")
        else:
            # لیست را به همراه Title چاپ می‌کنیم
            print("Here are the notes you just created:")
            for note_id, note_title in created_notes_info:
                print(f"  - Title: \"{note_title}\" (ID: {note_id})")

            id_to_get = input("Enter the ID of the note you want to retrieve: ")

            get_request = notes_pb2.GetNoteRequest(id=id_to_get)

            try:
                get_response = stub.GetNote(get_request)
                if get_response.note.id:
                    print("✅ Note found:")
                    print(f"  ID: {get_response.note.id}")
                    print(f"  Title: {get_response.note.title}")
                    print(f"  Content: {get_response.note.content}")
                else:
                    print("❌ Error: Server returned an empty note response.")
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    print(f"❌ Error: Note with ID '{id_to_get}' not found.")
                else:
                    print(f"❌ Error getting note: {e.details()}")

        # --- 3. List All Notes ---
        print("\n--- 3. List All Notes ---")
        list_request = notes_pb2.ListNotesRequest()
        try:
            list_response = stub.ListNotes(list_request)
            if not list_response.notes:
                print("ℹ️ No notes found in the database.")
            else:
                print(f"✅ Found {len(list_response.notes)} total note(s):")
                for note in list_response.notes:
                    print(f"  - [{note.id}] {note.title}")
        except grpc.RpcError as e:
            print(f"❌ Error listing notes: {e.details()}")

        # --- 4. Delete Note (Based on user ID prompt) ---
        print("\n--- 4. Delete a Specific Note ---")
        id_to_delete = input("Enter the ID of the note you want to delete: ")

        delete_request = notes_pb2.DeleteNoteRequest(id=id_to_delete)

        try:
            delete_response = stub.DeleteNote(delete_request)
            if delete_response.success:
                print(f"✅ Success: {delete_response.message}")
            else:
                print(f"❌ Error: {delete_response.message} (Perhaps the ID was incorrect?)")
        except grpc.RpcError as e:
            print(f"❌ Error deleting note: {e.details()}")

        # --- 5. Final List (To show deletion) ---
        print("\n--- 5. Final List of All Notes (After Deletion) ---")
        try:
            final_list_response = stub.ListNotes(notes_pb2.ListNotesRequest())
            if not final_list_response.notes:
                print("ℹ️ No notes remaining in the database.")
            else:
                print(f"✅ Found {len(final_list_response.notes)} remaining note(s):")
                for note in final_list_response.notes:
                    print(f"  - [{note.id}] {note.title}")
        except grpc.RpcError as e:
            print(f"❌ Error listing final notes: {e.details()}")


if __name__ == '__main__':
    run()