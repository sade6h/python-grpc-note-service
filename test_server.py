import pytest
import grpc
import server
import database  # ما هنوز به این فایل برای import شدن نیاز داریم
import notes_pb2
import sqlite3
from pytest_mock import MockerFixture

# This is the 'pytest-mock' fixture
from pytest_mock import MockerFixture


# This fixture runs once before each test function
@pytest.fixture
def service(monkeypatch, mocker: MockerFixture):

    conn = sqlite3.connect(":memory:")

    conn.row_factory = sqlite3.Row


    create_table_query = """
                         CREATE TABLE IF NOT EXISTS notes \
                         ( \
                             id \
                             TEXT \
                             PRIMARY \
                             KEY, \
                             title \
                             TEXT \
                             NOT \
                             NULL, \
                             content \
                             TEXT
                         ); \
                         """
    conn.execute(create_table_query)
    conn.commit()

    note_service = server.NoteService()

    monkeypatch.setattr(note_service, "get_db_connection", lambda: conn)

    yield note_service

    conn.close()

def test_create_note(service: server.NoteService, mocker: MockerFixture):
    # Create a mock gRPC context (needed by the function signature)
    mock_context = mocker.Mock()

    # Create the request message
    request = notes_pb2.CreateNoteRequest(
        title="Test Note",
        content="This is a test."
    )

    # Call the service method directly
    response = service.CreateNote(request, mock_context)

    # Assert the response
    assert response.id is not None
    assert len(response.id) == 36  # UUID length


def test_get_note(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()

    # 1. First, create a note to test against
    create_request = notes_pb2.CreateNoteRequest(title="Get Me", content="Test")
    create_response = service.CreateNote(create_request, mock_context)

    # 2. Now, create a GetNote request
    get_request = notes_pb2.GetNoteRequest(id=create_response.id)

    # 3. Call the GetNote method
    get_response = service.GetNote(get_request, mock_context)

    # 4. Assert the response
    assert get_response.note.id == create_response.id
    assert get_response.note.title == "Get Me"
    assert get_response.note.content == "Test"


def test_get_note_not_found(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()

    # Request an ID that does not exist
    request = notes_pb2.GetNoteRequest(id="non-existent-uuid")

    response = service.GetNote(request, mock_context)

    # Check that the error context was set correctly
    mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)

    # Check that the returned note is empty
    assert response.note.id == ""


def test_list_notes(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()

    # 1. Check that the list is initially empty
    list_req_empty = notes_pb2.ListNotesRequest()
    list_res_empty = service.ListNotes(list_req_empty, mock_context)
    assert len(list_res_empty.notes) == 0

    # 2. Create two notes
    service.CreateNote(notes_pb2.CreateNoteRequest(title="Note 1"), mock_context)
    service.CreateNote(notes_pb2.CreateNoteRequest(title="Note 2"), mock_context)

    # 3. List the notes
    list_req_full = notes_pb2.ListNotesRequest()
    list_res_full = service.ListNotes(list_req_full, mock_context)

    # 4. Assert
    assert len(list_res_full.notes) == 2
    assert list_res_full.notes[0].title == "Note 1"
    assert list_res_full.notes[1].title == "Note 2"


def test_delete_note(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()

    # 1. Create a note
    create_res = service.CreateNote(
        notes_pb2.CreateNoteRequest(title="To Be Deleted"),
        mock_context
    )

    # 2. Delete the note
    delete_req = notes_pb2.DeleteNoteRequest(id=create_res.id)
    delete_res = service.DeleteNote(delete_req, mock_context)

    # 3. Assert the delete was successful
    assert delete_res.success == True
    assert "Deleted successfully" in delete_res.message

    # 4. Verify it's really gone
    get_req = notes_pb2.GetNoteRequest(id=create_res.id)
    get_res = service.GetNote(get_req, mock_context)

    # The 'GetNote' method should now set the context to NOT_FOUND
    mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
    assert get_res.note.id == ""


def test_delete_note_not_found(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()

    # Try to delete a non-existent ID
    delete_req = notes_pb2.DeleteNoteRequest(id="non-existent-uuid")
    delete_res = service.DeleteNote(delete_req, mock_context)

    # Assert the delete failed correctly
    assert delete_res.success == False
    assert "Note ID not found" in delete_res.message