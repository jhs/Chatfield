"""FastAPI server for Chatfield conversational data collection."""

import sys
import traceback
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from ..interviewer import Interviewer
from .interview import interview


class InterviewSession:
    """Manages a single interview session."""

    def __init__(self, thread_id: str):
        """Initialize session with the predefined interview."""
        self.interview = interview
        self.interviewer = Interviewer(self.interview, thread_id=thread_id)
        self.thread_id = thread_id

    def send_message(self, message: Optional[str]) -> tuple[str, bool]:
        """
        Send message to interviewer and get response.

        Returns:
            Tuple of (response_message, is_done)
        """
        response = self.interviewer.go(message)
        return response, self.interview._done

    def get_results(self) -> str:
        """Get pretty-printed interview results."""
        return self.interview._pretty()


# Global session for single-interview mode
current_session: Optional[InterviewSession] = None


# Request/Response models
class StartInterviewRequest(BaseModel):
    thread_id: Optional[str] = None


class StartInterviewResponse(BaseModel):
    thread_id: str
    message: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    done: bool
    results: Optional[str] = None


# Create FastAPI app
app = FastAPI(title="Chatfield Server")


# Global exception handler - prints full tracebacks to stderr
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and log them to stderr."""
    print(f"\n{'='*60}", file=sys.stderr, flush=True)
    print(f"ERROR: {request.method} {request.url}", file=sys.stderr, flush=True)
    print(f"Exception type: {type(exc).__name__}", file=sys.stderr, flush=True)
    print(f"{'='*60}", file=sys.stderr, flush=True)
    traceback.print_exc(file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr, flush=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


@app.post("/api/start", response_model=StartInterviewResponse)
async def start_interview(request: StartInterviewRequest):
    """Initialize a new interview session."""
    global current_session

    thread_id = request.thread_id or f"session-{id(request)}"

    try:
        print(f"Starting interview: {thread_id}", file=sys.stderr, flush=True)
        current_session = InterviewSession(thread_id)
        first_message, _ = current_session.send_message(None)

        print(f"Interview started successfully: {thread_id}", file=sys.stderr, flush=True)

        return StartInterviewResponse(
            thread_id=thread_id,
            message=first_message
        )
    except Exception as e:
        print(f"\nERROR in start_interview:", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        print(f"", file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message in the active interview."""
    global current_session

    if not current_session:
        raise HTTPException(status_code=404, detail="No active interview")

    try:
        response, done = current_session.send_message(request.message)

        result = ChatResponse(response=response, done=done)

        if done:
            # Include results in response for API consumers
            results = current_session.get_results()
            result.results = results

        return result
    except Exception as e:
        print(f"\nERROR in chat:", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        print(f"", file=sys.stderr, flush=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def get_ui():
    """Serve the HTML chat interface."""
    template_path = Path(__file__).parent / "templates" / "chat.html"
    return template_path.read_text()


# HTML UI is now loaded from templates/chat.html
