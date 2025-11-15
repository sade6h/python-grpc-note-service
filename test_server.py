import pytest
import grpc
import server
import database
import notes_pb2
import sqlite3
from pytest_mock import MockerFixture

@pytest.fixture
def service(monkeypatch, mocker: MockerFixture):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_table_query = """
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT
    );
    """
    conn.execute(create_table_query)
    conn.commit()
    note_service = server.NoteService()
    monkeypatch.setattr(note_service, "get_db_connection", lambda: conn)
    yield note_service
    conn.close()

# --- توابع تست ---

def test_create_note(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()
    request = notes_pb2.CreateNoteRequest(title="Test Note", content="This is a test.")
    response = service.CreateNote(request, mock_context)
    assert response.id is not None
    assert len(response.id) == 36

def test_get_note(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()
    create_response = service.CreateNote(notes_pb2.CreateNoteRequest(title="Get Me"), mock_context)
    get_request = notes_pb2.GetNoteRequest(id=create_response.id)
    get_response = service.GetNote(get_request, mock_context)
    assert get_response.note.id == create_response.id

def test_get_note_not_found(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()
    request = notes_pb2.GetNoteRequest(id="non-existent-uuid")
    response = service.GetNote(request, mock_context)
    mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)
    assert response.note.id == ""

def test_list_notes(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()
    service.CreateNote(notes_pb2.CreateNoteRequest(title="Note 1"), mock_context)
    service.CreateNote(notes_pb2.CreateNoteRequest(title="Note 2"), mock_context)
    list_response = service.ListNotes(notes_pb2.ListNotesRequest(), mock_context)
    assert len(list_response.notes) == 2

def test_delete_note(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()
    create_res = service.CreateNote(notes_pb2.CreateNoteRequest(title="To Be Deleted"), mock_context)
    delete_req = notes_pb2.DeleteNoteRequest(id=create_res.id)
    delete_res = service.DeleteNote(delete_req, mock_context)
    assert delete_res.success == True
    get_req = notes_pb2.GetNoteRequest(id=create_res.id)
    service.GetNote(get_req, mock_context)
    mock_context.set_code.assert_called_with(grpc.StatusCode.NOT_FOUND)

def test_delete_note_not_found(service: server.NoteService, mocker: MockerFixture):
    mock_context = mocker.Mock()
    delete_req = notes_pb2.DeleteNoteRequest(id="non-existent-uuid")
    delete_res = service.DeleteNote(delete_req, mock_context)
    assert delete_res.success == False
    assert "Note ID not found" in delete_res.message

# --- تست‌های Search حذف شدند ---