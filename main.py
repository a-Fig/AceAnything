#  python -m uvicorn main:app --reload

import os
import uuid
import json
import copy
import re # Add import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from threading import Thread # Changed from multiprocessing
import queue # For thread-safe queue
import asyncio
import time # Added for sleep in worker
import base64
import tempfile
from dotenv import load_dotenv
import os

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
# Removed BackgroundTasks as it's no longer used by initiate_quiz_generation
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware  # For simple session management
from starlette.middleware.base import BaseHTTPMiddleware
# If you were to use itsdangerous for signed cookies directly:
# from starlette.requests import Request as StarletteRequest
# from itsdangerous import URLSafeSerializer, BadSignature

# Assuming your classes are in these files
import quizclass as qc
import questionclass as q_cl  # Renamed to avoid conflict if any
import chatapi # Ensure chatapi is imported

# Import the quiz objects directly
from premade_quizzes.premade_quizzes import quiz_traffic_laws as california_driving_quiz
from premade_quizzes.premade_quizzes import quiz_ap_us_history # New
from premade_quizzes.premade_quizzes import quiz_usa_citizens_test # New
# from premade_quizzes.premade_quizzes import all_premade_quizzes # Alternative if you want to use the list

print("main.py")
# Ensure chatapi and tooled_llm are available in the same directory or Python path
# import chatapi
# import tooled_llm


# --- Configuration ---
load_dotenv()
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
# SERIALIZER = URLSafeSerializer(SESSION_SECRET_KEY) # For itsdangerous

# --- Google Cloud Credentials Setup ---
# This should be one of the first things to run
gcp_creds_json_base64 = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON_BASE64")
if gcp_creds_json_base64:
    try:
        creds_json_str = base64.b64decode(gcp_creds_json_base64).decode("utf-8")
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", encoding='utf-8') as temp_creds_file:
            temp_creds_file.write(creds_json_str)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_file.name
            print(f"Successfully set GOOGLE_APPLICATION_CREDENTIALS from env var to: {temp_creds_file.name}")
    except Exception as e_gcp_creds:
        print(f"CRITICAL ERROR: Failed to decode/write Google credentials from base64 env var: {e_gcp_creds}")
        # Depending on your app's needs, you might want to exit or raise a more severe error if creds are vital
else:
    print("INFO: GOOGLE_APPLICATION_CREDENTIALS_JSON_BASE64 env var not set. Assuming local ADC or other auth method.")


# --- Persistent Data Directory Setup (for Render Disks or local fallback) ---
# Base path for persistent storage, configurable via environment variable for Render
# Defaults to a local path if the environment variable isn't set (for local development)
RENDER_DISK_MOUNT_PATH_BASE = os.environ.get("RENDER_DISK_MOUNT_PATH", str(Path(__file__).parent))
DATA_DIR_NAME = "quizdata_persistent"
DATA_DIR = Path(RENDER_DISK_MOUNT_PATH_BASE) / DATA_DIR_NAME

UPLOADS_DIR_NAME = "uploads_temp"
UPLOADS_DIR = Path(RENDER_DISK_MOUNT_PATH_BASE) / UPLOADS_DIR_NAME # Also place uploads on persistent/configurable disk path

def ensure_directory_exists(dir_path: Path, dir_name: str):
    if not dir_path.exists():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Successfully created {dir_name} directory at {dir_path}")
        except Exception as e_dir:
            print(f"CRITICAL ERROR: Could not create {dir_name} directory at {dir_path}: {e_dir}")
            # Potentially raise an error or handle appropriately if these dirs are essential

ensure_directory_exists(DATA_DIR, "DATA_DIR")
ensure_directory_exists(UPLOADS_DIR, "UPLOADS_DIR")


# --- App Initialization ---
app = FastAPI()

# Mount static files
static_dir = Path(__file__).parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
# Use custom StaticFiles to add cache control headers
from fastapi.staticfiles import StaticFiles
class NoCacheStaticFiles(StaticFiles):
    async def __call__(self, scope, receive, send):
        response = await super().__call__(scope, receive, send)
        if hasattr(response, 'headers'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response

app.mount("/static", NoCacheStaticFiles(directory=static_dir), name="static")

# Mount templates
templates_dir = Path(__file__).parent / "templates"
if not templates_dir.exists():
    templates_dir.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Create a logging middleware to log all requests
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log the request
        print(f"Request: {request.method} {request.url.path}")
        print(f"Client: {request.client}")
        print(f"Headers: {request.headers}")

        # Process the request and get the response
        response = await call_next(request)

        # Log the response
        process_time = time.time() - start_time
        print(f"Response: {response.status_code} - Took {process_time:.4f}s")

        return response

# Add the logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add session middleware (stores session data in a signed cookie)
# Note: SessionMiddleware is basic. For production, consider more robust session management.
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

# In-memory storage for active sessions
# Keyed by session_id
# In a production environment, you'd use a database or a distributed cache like Redis.
active_sessions: Dict[str, Dict[str, Any]] = {} # Explicitly type hint for clarity

# Available quizzes (This remains for default quiz info, not instances)
# THIS QUIZZES DICTIONARY SEEMS REDUNDANT given DEFAULT_QUIZZES_INFO later on.
# Consider removing or refactoring to use only DEFAULT_QUIZZES_INFO if it serves the same purpose.
QUIZZES = {
    "california_driving": {
        "title": "DMV Test Prep: Road Rules & Signs",
        "description": "Practice for your driver's license test with questions about road rules, traffic signs, and safe driving.",
        "quiz_object": california_driving_quiz
    },
    "ap_us_history": { # New
        "title": "AP US History Challenge",
        "description": "Test your knowledge of key events, figures, and concepts in American History from 1491 to the present.",
        "quiz_object": quiz_ap_us_history
    },
    "us_citizenship_test": { # New
        "title": "US Citizenship Test Practice",
        "description": "Prepare for the U.S. Naturalization Test with questions on American government, history, and civics.",
        "quiz_object": quiz_usa_citizens_test
    }
}

# We need the data directory for custom uploaded quizzes
# DATA_DIR = Path(__file__).parent / "data" # This line will be replaced/managed by the new setup above
# if not DATA_DIR.exists():
#     DATA_DIR.mkdir(parents=True, exist_ok=True)

def get_session_data(session_id: str) -> Dict[str, Any]:
    """Get or create session data for a given session_id."""
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            "user_quizzes": {},  # Stores Quiz objects (custom or copies of defaults)
            "current_quiz_instance_key": None, # Key to find the quiz in user_quizzes
            "current_quiz_instance": None,    # The actual Quiz object being played
            "current_tutor_instance": None,
            "tutor_initialized_by_worker": False, # New flag
            "tutor_init_failed": False,         # New flag
            "current_question_details": None, # Holds cat_idx, q_idx, type
            "current_score": {"correct": 0, "total": 0},
            "message_queue": [], # For tutor messages
        }
    # Ensure all keys are present for existing sessions if they were created before an update
    session_data = active_sessions[session_id]
    defaults = {
        "user_quizzes": {},
        "current_quiz_instance_key": None,
        "current_quiz_instance": None,
        "current_tutor_instance": None,
        "tutor_initialized_by_worker": False,
        "tutor_init_failed": False,
        "current_question_details": None,
        "current_score": {"correct": 0, "total": 0},
        "message_queue": [],
    }
    for key, default_value in defaults.items():
        if key not in session_data:
            session_data[key] = default_value
        # Ensure message_queue is a list
        if key == "message_queue" and not isinstance(session_data[key], list):
             session_data[key] = []


    return session_data

# --- Helper Functions ---
def get_session_id(request: Request) -> str:
    """Ensures a session ID exists and returns it."""
    if "session_id" not in request.session:
        request.session["session_id"] = str(uuid.uuid4())
    return request.session["session_id"]

def get_current_quiz_instance(session_id: str) -> Optional[qc.Quiz]:
    """Gets the currently active quiz instance for the session."""
    return get_session_data(session_id).get("current_quiz_instance")

def get_current_tutor_instance(session_id: str) -> Optional[qc.TutorLLM]:
    """Gets the tutor for the currently active quiz instance."""
    return get_session_data(session_id).get("current_tutor_instance")

def get_tutor_message_queue(session_id: str) -> List[str]:
    """Gets the message queue for the current session's tutor."""
    session_data = get_session_data(session_id)
    # Ensure message_queue is always initialized as a list
    if "message_queue" not in session_data or not isinstance(session_data["message_queue"], list):
        session_data["message_queue"] = []
    return session_data["message_queue"]


# Renamed and refactored from initialize_quiz_session
def initialize_quiz_session_dependencies(request: Request, session_id: str, quiz_instance_key: str):
    """
    Initializes tutor, score, current question, and session cookies
    for a quiz that is already loaded into session_data["user_quizzes"]
    and set as session_data["current_quiz_instance"].
    """
    session_data = get_session_data(session_id)
    current_quiz = session_data.get("current_quiz_instance")

    if not current_quiz:
        print(f"Error in initialize_quiz_session_dependencies: current_quiz_instance not set for key {quiz_instance_key}")
        request.session.pop("current_quiz_name", None)
        request.session.pop("current_quiz_title", None)
        # Potentially raise an error or handle this state more gracefully
        raise HTTPException(status_code=500, detail="Failed to initialize session: current quiz not found.")

    # Clear tutor instance and message queue before queuing initialization
    session_data["current_tutor_instance"] = None
    session_data["tutor_initialized_by_worker"] = False # Flag to indicate worker should initialize
    session_data["tutor_init_failed"] = False          # Reset failure flag

    session_message_queue = get_tutor_message_queue(session_id) # Ensures it's initialized
    session_message_queue.clear() # Clear any old messages

    # Queue the tutor initialization task
    task_queue.put({
        "task_type": "initialize_tutor",
        "session_id": session_id,
        "quiz_instance_key": quiz_instance_key
    })
    print(f"Tutor initialization for quiz {quiz_instance_key} (session {session_id}) queued for worker.")

    session_data["current_score"] = {"correct": 0, "total": 0}
    session_data["current_question_details"] = None
    
    # Update Starlette session cookies
    request.session["current_quiz_name"] = quiz_instance_key # This is the key in user_quizzes
    request.session["current_quiz_title"] = current_quiz.title if hasattr(current_quiz, 'title') else "Untitled Quiz"


# --- Default Quiz Loading ---
# We now load quizzes directly as Python objects from premade_quizzes.py

# Dictionary mapping quiz names to their metadata and ORIGINAL objects
DEFAULT_QUIZZES_INFO = {
    "california_driving": { # Moved california_driving to be consistent in order with js
        "title": "DMV Test Prep: Road Rules & Signs",
        "description": "Practice for your driver's license test with questions about road rules, traffic signs, and safe driving.",
        "quiz_object": california_driving_quiz,
        "icon": "car", # Assuming this was intended for california_driving
        "thumbnail": "default_quiz_3.jpg"
    },
    "ap_us_history": { # New
        "title": "AP US History Challenge",
        "description": "Test your knowledge of key events, figures, and concepts in American History from 1491 to the present.",
        "quiz_object": quiz_ap_us_history,
        "icon": "history", # Example icon key
        "thumbnail": "default_quiz_apush.jpg" # Example thumbnail
    },
    "us_citizenship_test": { # New
        "title": "US Citizenship Test Practice",
        "description": "Prepare for the U.S. Naturalization Test with questions on American government, history, and civics.",
        "quiz_object": quiz_usa_citizens_test,
        "icon": "government", # Example icon key
        "thumbnail": "default_quiz_citizenship.jpg" # Example thumbnail
    }
}

# We need the data directory for custom uploaded quizzes
# DATA_DIR = Path(__file__).parent / "data" # This line will be replaced/managed by the new setup above
# if not DATA_DIR.exists():
#     DATA_DIR.mkdir(parents=True, exist_ok=True)


# --- Global Task Queue ---
task_queue = queue.Queue()
WORKER_SENTINEL = object() # Used to signal the worker thread to stop

# --- FastAPI Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the quiz selection page.
    Lists default quizzes and custom quizzes specific to the current user/session.
    """
    session_id = get_session_id(request) # Ensure session ID exists for user identification

    display_quizzes = {}

    # 1. Add default quizzes (available to all)
    #    The quiz_name_id for these will be their generic names (e.g., "world_war_2")
    #    The /api/start-quiz endpoint will handle creating session-specific copies.
    for key, data in DEFAULT_QUIZZES_INFO.items(): # Use DEFAULT_QUIZZES_INFO
        question_count = 0
        if data.get("quiz_object") and hasattr(data["quiz_object"], "get_total_question_count"):
            question_count = data["quiz_object"].get_total_question_count()
        elif data.get("quiz_object") and hasattr(data["quiz_object"], "section_bank"): # Fallback if method not there yet
            for section in data["quiz_object"].section_bank:
                question_count += len(section.questions)

        display_quizzes[key] = {
            "title": data["title"],
            "description": data["description"],
            "is_custom": False,
            "quiz_name_id": key, # Generic key for default quizzes
            "icon": data.get("icon"), # Add icon if available
            "thumbnail": data.get("thumbnail"), # Add thumbnail if available
            "question_count": question_count
        }

    # 2. Discover and add custom quizzes for the current session/user
    #    Custom quiz files are named like "{session_id}_custom_xxxx.json"
    #    The quiz_name_id for these will be their full filename stem.
    user_custom_quiz_pattern = f"{session_id}_custom_*.json"
    custom_quiz_files = list(DATA_DIR.glob(user_custom_quiz_pattern))

    for quiz_file_path in custom_quiz_files:
        try:
            with open(quiz_file_path, 'r') as f:
                quiz_data = json.load(f)
            
            # quiz_file.stem is the filename without .json (e.g., "{session_id}_custom_xxxx")
            # This is the ID that will be used in the URL for /api/start-quiz/
            quiz_id = quiz_file_path.stem 
            
            quiz_title = quiz_data.get("title", "Custom Quiz") 
            # Provide a default or extract from source if description is missing
            description = quiz_data.get("description") # Description from quiz JSON if available
            if not description:
                 source_material_snippet = quiz_data.get("source_material", "Uploaded content.")[:100]
                 description = f"Custom quiz from: {source_material_snippet}..." if source_material_snippet else "A custom generated quiz."

            custom_question_count = 0
            if "sections" in quiz_data:
                for section in quiz_data["sections"]:
                    custom_question_count += len(section.get("questions", []))

            display_quizzes[quiz_id] = { # Use the unique quiz_id as key
                "title": quiz_title,
                "description": description,
                "is_custom": True,
                "quiz_name_id": quiz_id, # This ID is already user-specific
                "icon": "static/images/custom_quiz_icon.svg", # Example path, ensure exists
                "thumbnail": "static/images/custom_quiz_default.png", # Example path, ensure exists
                "question_count": custom_question_count
            }
        except json.JSONDecodeError as e_json:
            print(f"Error decoding JSON for custom quiz {quiz_file_path.name} for session {session_id}: {e_json}")
        except Exception as e:
            print(f"Error loading custom quiz {quiz_file_path.name} for session {session_id}: {e}")
            # Optionally skip or add an error placeholder for this specific quiz

    return templates.TemplateResponse("main_quiz_selection.html", {
        "request": request,
        "quizzes": display_quizzes 
    })

@app.post("/api/start-quiz/{quiz_name_id_from_url}") # Renamed param for clarity
async def start_quiz(request: Request, quiz_name_id_from_url: str):
    """
    Initialize a new quiz session.
    For default quizzes, it creates a user-specific copy.
    For custom quizzes, it loads the user's specific quiz file.
    The quiz_name_id_from_url for custom quizzes is expected to be already
    prefixed with session_id (e.g., sessionid_custom_xxxx).
    For default quizzes, it's the generic name (e.g., "world_war_2").
    """
    session_id = get_session_id(request)
    session_data = get_session_data(session_id)
    
    quiz_instance_key: str = quiz_name_id_from_url 
    quiz_obj: Optional[qc.Quiz] = None
    quiz_title: str = "Unknown Quiz"

    # Determine the correct quiz_instance_key for user_quizzes dictionary
    # and check if this quiz is already loaded for this user in this session.
    
    is_custom_quiz_format = quiz_name_id_from_url.startswith(f"{session_id}_custom_")
    is_default_quiz_format = quiz_name_id_from_url in DEFAULT_QUIZZES_INFO

    if is_custom_quiz_format:
        # For custom quizzes, quiz_name_id_from_url is the direct key
        quiz_instance_key = quiz_name_id_from_url 
    elif is_default_quiz_format:
        # For default quizzes, create a session-specific key for the user's copy
        quiz_instance_key = f"default_{session_id}_{quiz_name_id_from_url}"
    # else: it will be handled by the not found logic later if neither format matches

    if quiz_instance_key in session_data["user_quizzes"]:
        quiz_obj = session_data["user_quizzes"][quiz_instance_key]
        if quiz_obj and hasattr(quiz_obj, 'title'): 
             quiz_title = quiz_obj.title
        else:
            quiz_title = "Recovered Quiz (title missing)" # Fallback
        print(f"Resuming quiz '{quiz_title}' (key: {quiz_instance_key}) from active session.")
    else:
        # Quiz not in session_data["user_quizzes"], so load or create it.
        if is_custom_quiz_format: # quiz_name_id_from_url is already session_id_custom_xxxx
            quiz_file_path = DATA_DIR / f"{quiz_instance_key}.json" # use quiz_instance_key
            if not quiz_file_path.exists():
                print(f"Error: Custom quiz file not found: {quiz_file_path}")
                raise HTTPException(status_code=404, detail=f"Custom quiz '{quiz_instance_key}' not found.")
            try:
                with open(quiz_file_path, 'r') as f:
                    quiz_data_dict = json.load(f)
                quiz_obj = qc.Quiz.from_dict(quiz_data_dict)
                quiz_title = quiz_obj.title if hasattr(quiz_obj, 'title') and quiz_obj.title else "Custom Quiz (untitled)"
                quiz_obj.title = quiz_title # Ensure it's set on the object
                print(f"Loaded custom quiz '{quiz_title}' (key: {quiz_instance_key})")
            except Exception as e:
                print(f"Error loading custom quiz {quiz_instance_key} from {quiz_file_path}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to load custom quiz '{quiz_instance_key}'.")

        elif is_default_quiz_format: # quiz_name_id_from_url is generic like "world_war_2"
            original_quiz_info = DEFAULT_QUIZZES_INFO[quiz_name_id_from_url]
            quiz_obj = copy.deepcopy(original_quiz_info["quiz_object"])
            quiz_title = original_quiz_info["title"]
            if hasattr(quiz_obj, 'title'): # quiz_object from premade should have title attribute
                quiz_obj.title = quiz_title 
            print(f"Created new copy for default quiz '{quiz_title}' (key: {quiz_instance_key})")
        else:
            # Neither a recognized custom quiz format for this session, nor a known default quiz
            raise HTTPException(status_code=404, detail=f"Quiz '{quiz_name_id_from_url}' not found or not accessible for this session.")

    if not quiz_obj:
        raise HTTPException(status_code=500, detail=f"Failed to obtain or create quiz object for '{quiz_name_id_from_url}'.")

    # Store the quiz object in the user's session-specific quiz store
    session_data["user_quizzes"][quiz_instance_key] = quiz_obj
    
    # Set this quiz as the currently active one for the session
    session_data["current_quiz_instance_key"] = quiz_instance_key
    session_data["current_quiz_instance"] = quiz_obj
    
    # Initialize other session details (tutor, score, etc.) for this quiz
    # This call will use current_quiz_instance set above
    initialize_quiz_session_dependencies(request, session_id, quiz_instance_key)
    
    # The quiz_title for the response should be from the actual quiz_obj
    final_quiz_title = quiz_obj.title if hasattr(quiz_obj, 'title') and quiz_obj.title else "Quiz Started"

    return {"status": "success", "quiz_name": quiz_instance_key, "quiz_title": final_quiz_title}

@app.get("/quiz/{quiz_name_id}")
async def quiz_page(request: Request, quiz_name_id: str):
    """Serve the quiz interface page."""
    session_id = get_session_id(request)
    session_data = get_session_data(session_id)
    
    active_quiz = session_data.get("current_quiz_instance")
    if not active_quiz:
        raise HTTPException(status_code=400, detail="No active quiz session. Please select a quiz first.")

    # Ensure the quiz being accessed matches the one in session if it's a direct navigation
    # or if the user is trying to access a different quiz URL than the one started.
    # The current_quiz_name in session should be the source of truth for the active quiz.
    if request.session.get("current_quiz_name") != quiz_name_id:
        # This could happen if user manually changes URL. Redirect or error.
        # For now, let's assume start_quiz correctly set the session.
        # If needed, add a redirect to / or to /quiz/{session_quiz_name}
        print(f"Warning: URL quiz_name_id '{quiz_name_id}' does not match session's current_quiz_name '{request.session.get('current_quiz_name')}'.")
        # Consider aligning or raising error. For now, trust session.
        # raise HTTPException(status_code=400, detail="URL does not match active quiz session.")


    current_quiz_title = request.session.get("current_quiz_title", "Quiz") # Fallback title
    total_question_count = 0
    if active_quiz and hasattr(active_quiz, "get_total_question_count"):
        total_question_count = active_quiz.get_total_question_count()

    return templates.TemplateResponse("quiz_interface.html", {
        "request": request,
        "quiz_name": quiz_name_id, 
        "quiz_title": current_quiz_title,
        "total_question_count": total_question_count
    })

@app.get("/api/question")
async def get_question(request: Request):
    """Get the next question"""
    session_id = request.session["session_id"]
    session_data = get_session_data(session_id)
    quiz = session_data["current_quiz_instance"]
    
    if not quiz:
        return JSONResponse({"error": "No active quiz"}, status_code=400)
    
    try:
        # Determine if it's the first question of this session for this quiz
        is_first = session_data["current_score"]["total"] == 0
        cat_idx, q_idx = quiz.pick_question(is_first_question=is_first)
        question = quiz.get_question(cat_idx, q_idx)
        
        # Determine question type more explicitly
        question_type_str = "unknown"
        if isinstance(question, q_cl.TrueFalseQuestion):
            question_type_str = "tf"  # Use "tf" for True/False
        elif isinstance(question, q_cl.MultipleChoice): # Must be after TrueFalseQuestion check as TFQ is a subclass
            question_type_str = "mcq"
        elif isinstance(question, q_cl.ShortAnswer):
            question_type_str = "short_answer"
        else:
            # Fallback, though ideally all question types should be covered
            question_type_str = question.__class__.__name__.lower()

        # Store current question info in session
        session_data["current_question_details"] = {
            "cat_idx": cat_idx,
            "q_idx": q_idx,
            "type": question_type_str 
        }

        options = []
        # build_parts() is safe for MCQ and its subclass TrueFalseQuestion
        if isinstance(question, q_cl.MultipleChoice): 
            _, options = question.build_parts()
        
        return {
            "text": question.question,
            "type": question_type_str,
            "options": options,
            "score": session_data["current_score"]
        }
    except ValueError as e: # Catch potential errors from pick_question if no questions/sections
        return JSONResponse({"error": str(e)}, status_code=500)
    except Exception as e:
        # Log the exception for more detailed debugging on the server side
        print(f"Error in /api/question: {type(e).__name__} - {e}")
        return JSONResponse({"error": "An unexpected error occurred while fetching the question."}, status_code=500)

@app.post("/api/submit")
async def submit_answer(request: Request, answer: dict):
    """Submit and grade an answer"""
    session_id = request.session["session_id"]
    session_data = get_session_data(session_id)
    quiz = session_data.get("current_quiz_instance")

    if not quiz:
        return JSONResponse({"error": "No active quiz found in session"}, status_code=400)

    current_question_details = session_data.get("current_question_details")
    if not current_question_details:
        return JSONResponse({"error": "No active question details found in session"}, status_code=400)
    
    cat_idx = current_question_details.get("cat_idx")
    q_idx = current_question_details.get("q_idx")
    # question_type = current_question_details.get("type") # Type is stored, can be used if needed

    if cat_idx is None or q_idx is None:
        return JSONResponse({"error": "Invalid question details in session (cat_idx or q_idx missing)"}, status_code=400)

    try:
        # Correctly retrieve the question object using the stored indices
        question = quiz.get_question(cat_idx, q_idx)
    except (IndexError, TypeError, AttributeError) as e: # Added AttributeError for robustness
        print(f"Error retrieving question object with cat_idx {cat_idx}, q_idx {q_idx}: {e}")
        return JSONResponse({"error": "Could not retrieve current question from quiz. Details might be invalid or quiz structure issue."}, status_code=500)
    
    if question is None: # Explicitly check if the question object was not found
        print(f"Question object is None for cat_idx {cat_idx}, q_idx {q_idx}. Check quiz data and indices.")
        return JSONResponse({"error": "Failed to load question object. It may not exist at the specified indices."}, status_code=500)
        
    user_answer_data = answer.get("answer")
    if user_answer_data is None: # Check if answer is provided
        return JSONResponse({"error": "No answer provided in submission"}, status_code=400)
    
    # Grade the answer
    score_value, feedback_str = question.grade_answer(user_answer_data)
    is_correct = score_value > 0.8
    
    # Update score in session
    session_data["current_score"]["total"] += 1
    if is_correct:
        session_data["current_score"]["correct"] += 1
    
    # Get tutor feedback / context setting
    tutor = session_data.get("current_tutor_instance")
    
    # Always clear the session's message queue for the tutor before potentially calling it.
    if "message_queue" in session_data:
        session_data["message_queue"].clear()
    else:
        session_data["message_queue"] = [] # Ensure it exists

    if tutor:
        if not is_correct:
            # Construct the prompt for the tutor for incorrect answers
            prompt_text = f'''Question: {question.rebuild_question()}
Student answer: {user_answer_data}
Correct answer: {question.correct_answer if hasattr(question, 'correct_answer') else 'N/A'}
Explanation: {question.explanation if hasattr(question, 'explanation') else 'N/A'}'''
            try:
                tutor.prompt(prompt_text) # This populates session_data["message_queue"]
            except Exception as e:
                print(f"Error during tutor prompt for incorrect answer: {e}")
                session_data["message_queue"].append("Sorry, the tutor encountered an error trying to provide feedback.")
        else:
            # Answer is correct.
            # Inform the tutor about the correct submission for context.
            context_prompt = (
                f"Context: The student just answered the following question correctly.\n"
                f"Question: {question.rebuild_question()}\n"
                f"Student's (correct) answer: {user_answer_data}\n"
                f"Explanation: {question.explanation if hasattr(question, 'explanation') else 'N/A'}\n"
                f"This is for your context. No immediate response to the user is needed for this correct answer. Be prepared for potential follow-up questions from the user regarding this topic."
            )
            try:
                tutor.prompt(context_prompt)
                # Clear messages after context prompt for correct answer.
                if "message_queue" in session_data:
                    session_data["message_queue"].clear()
            except Exception as e:
                print(f"Error informing tutor of correct answer (context setting): {e}")

    final_feedback = feedback_str if feedback_str else (question.explanation if hasattr(question, 'explanation') else "No additional feedback.")
    
    tutor_messages_for_response = list(session_data["message_queue"])

    return {
        "correct": is_correct,
        "score": session_data["current_score"],
        "feedback": final_feedback,
        "tutor_messages": tutor_messages_for_response 
    }

# Hypothetical import for LLM utility (would need to be a real module/function)
# from .llm_utils import generate_title_with_llm 

async def generate_and_save_quiz_task(
    source_material: str, 
    requested_quiz_title: str, # User's requested title, could be empty
    custom_quiz_filepath: Path, 
    temp_pdf_path: Path,
    quiz_id_stem: str, # For logging
    quiz_size_preference: Optional[str] = None
):
    """Background task to generate AI quiz, potentially generate a title, and save it."""
    final_quiz_title = requested_quiz_title.strip() if requested_quiz_title else ""

    def _generate_short_fallback_title(src_material_snippet: str, q_id_stem: str) -> str:
        # Remove common PDF page markers like "-- Page X --"
        cleaned_snippet = re.sub(r"--\s*Page\s*\d+\s*--", "", src_material_snippet, flags=re.IGNORECASE)
        # Remove leading non-alphanumeric characters (except spaces to preserve word separation)
        # and common document start patterns that are not good for titles.
        cleaned_snippet = re.sub(r"^[^a-zA-Z0-9_]+(?=[a-zA-Z0-9_])", "", cleaned_snippet.strip()).strip()
        # Further clean typical intro phrases if they are at the very beginning
        common_poor_starts = ["this document", "this paper", "the following text", "abstract", "introduction"]
        for poor_start in common_poor_starts:
            if cleaned_snippet.lower().startswith(poor_start):
                cleaned_snippet = cleaned_snippet[len(poor_start):].strip()
                cleaned_snippet = re.sub(r"^[^a-zA-Z0-9_]+(?=[a-zA-Z0-9_])", "", cleaned_snippet.strip()).strip() # Clean again after removing prefix

        words = cleaned_snippet.split()
        
        meaningful_words = [word for word in words if len(word) > 2 and word.isalpha()] 
        if not meaningful_words and words: # If filtering removed all words, use original (but cleaned) words if any
            meaningful_words = [word for word in words if word.strip()] # Use any non-empty words

        num_words_to_take = min(len(meaningful_words), 3) 
        if num_words_to_take == 0:
            return f"Custom Quiz {q_id_stem.split('_')[-1]}"

        short_title_words = meaningful_words[:num_words_to_take]
        
        # Capitalize words for title case, unless word is all caps (acronym)
        title_cased_words = []
        for word in short_title_words:
            if word.isupper():
                title_cased_words.append(word)
            else:
                title_cased_words.append(word.capitalize())
        final_short_title = " ".join(title_cased_words)

        if not final_short_title.strip() or len(final_short_title) < 3:
            return f"Custom Quiz {q_id_stem.split('_')[-1]}"
            
        return final_short_title

    try:
        if not final_quiz_title:
            print(f"Background task for {quiz_id_stem}: No title provided by user. Attempting LLM generation.")
            try:
                source_snippet_for_llm_title = source_material[:2000].replace("\n", " ").strip()
                
                title_prompt = f"""Analyze the following text snippet.
Your ONLY task is to generate a concise, engaging, and relevant title for a quiz based on this text.
The title MUST be between 1 and 5 words long.
Your response MUST contain ONLY the generated title and NOTHING ELSE.
Do NOT include any introductory phrases such as "Here is a title:", "The title is:", "Title:", or similar.
Do NOT include quotation marks (single or double) around the title in your response.

Text snippet:
```
{source_snippet_for_llm_title}
```

Respond with ONLY the title. 
For example, if the text is about World War II history, a good response is: World War II Events
A bad response would be: Title: "World War II Events" 
"""
                title_llm = chatapi.FlashChat(instruction_prompt="You are an expert quiz title generator. Your sole purpose is to generate a short, relevant quiz title based on provided text and return ONLY the title.")
                llm_response = title_llm.prompt(title_prompt)

                if llm_response and isinstance(llm_response, str) and llm_response.strip():
                    generated_title = llm_response.strip()

                    # More robust cleaning of prefixes and quotes
                    prefixes_to_remove = [
                        "title:", "quiz title:", "here's a title:", 
                        "here is a title:", "the title is:", "generated title:"
                    ]
                    for prefix in prefixes_to_remove:
                        if generated_title.lower().startswith(prefix):
                            generated_title = generated_title[len(prefix):].strip()
                    
                    # Remove surrounding quotes (single or double) more carefully
                    if generated_title.startswith('"') and generated_title.endswith('"') and len(generated_title) > 1:
                        generated_title = generated_title[1:-1]
                    elif generated_title.startswith("'") and generated_title.endswith("'") and len(generated_title) > 1:
                        generated_title = generated_title[1:-1]
                    
                    final_quiz_title = generated_title.strip() # Final strip for safety

                    if final_quiz_title: # Check if title is not empty after all cleaning
                        print(f"Background task for {quiz_id_stem}: LLM generated title successfully processed: '{final_quiz_title}'")
                    else:
                        print(f"Background task for {quiz_id_stem}: LLM response was empty after cleaning. Using improved fallback.")
                        snippet_for_fallback = source_material[:300]
                        final_quiz_title = _generate_short_fallback_title(snippet_for_fallback, quiz_id_stem)
                else:
                    print(f"Background task for {quiz_id_stem}: LLM title generation did not return a valid string or was empty. Using improved fallback.")
                    snippet_for_fallback = source_material[:300]
                    final_quiz_title = _generate_short_fallback_title(snippet_for_fallback, quiz_id_stem)
            except Exception as e_llm:
                print(f"Background task for {quiz_id_stem}: LLM title generation failed: {type(e_llm).__name__} - {e_llm}. Using improved fallback title.")
                snippet_for_fallback = source_material[:300]
                final_quiz_title = _generate_short_fallback_title(snippet_for_fallback, quiz_id_stem)
        else:
            # User provided a title, so no need to generate with LLM or use fallback.
            print(f"Background task for {quiz_id_stem}: User provided title: '{final_quiz_title}'. Skipping LLM generation.")


        print(f"Background task started for {quiz_id_stem}: Generating quiz with final chosen title '{final_quiz_title}' for {custom_quiz_filepath}")
        
        # Determine target quiz size based on preference
        target_quiz_size: Optional[int] = None
        if quiz_size_preference == "small":
            target_quiz_size = 10
        elif quiz_size_preference == "medium":
            target_quiz_size = 20
        elif quiz_size_preference == "large":
            target_quiz_size = 30
        # If None or "auto" or any other value, generate_ai_quiz will use its default (suggested_quiz_size)
        
        print(f"[Quiz Size - {quiz_id_stem}] Preference: '{quiz_size_preference}', Target number of questions: {target_quiz_size if target_quiz_size is not None else 'Auto'}")

        # Ensure qc.generate_ai_quiz can accept quiz_title and uses it internally
        new_quiz = qc.generate_ai_quiz(
            source_material=source_material, 
            quiz_title=final_quiz_title, 
            quiz_size=target_quiz_size, # Pass the determined size
            print_debug=False
        )
        
        if not new_quiz or not new_quiz.section_bank or not any(s.questions for s in new_quiz.section_bank):
            print(f"Error in background task ({quiz_id_stem}): Failed to generate any questions for quiz '{final_quiz_title}'.")
            # Consider writing an error status file, e.g.:
            # custom_quiz_filepath.with_suffix('.error').write_text("Failed to generate questions.")
            return

        # Explicitly set the title on the quiz object before saving, in case generate_ai_quiz doesn't assign it from param
        new_quiz.title = final_quiz_title 

        with open(custom_quiz_filepath, "w") as f:
            json.dump(new_quiz.to_dict(), f, indent=4)
        print(f"Background task completed for {quiz_id_stem}: Quiz '{final_quiz_title}' saved to {custom_quiz_filepath}")

    except Exception as e:
        print(f"Error in background quiz generation for {quiz_id_stem} ('{final_quiz_title}', {custom_quiz_filepath}): {type(e).__name__} - {e}")
        # Optionally, save an error marker or status file, e.g.:
        # custom_quiz_filepath.with_suffix('.error').write_text(f"{type(e).__name__}: {e}")
    finally:
        # Clean up the temporary PDF file
        if temp_pdf_path.exists():
            try:
                temp_pdf_path.unlink(missing_ok=True) # missing_ok=True added for robustness
                print(f"Background task for {quiz_id_stem}: Cleaned up temporary PDF {temp_pdf_path}")
            except Exception as e_unlink:
                print(f"Error cleaning up temp PDF {temp_pdf_path} in background task for {quiz_id_stem}: {e_unlink}")

# Synchronous wrapper for the async task
def run_generate_and_save_quiz_task_sync(
    source_material: str,
    requested_quiz_title: str,
    custom_quiz_filepath: Path,
    temp_pdf_path: Path,
    quiz_id_stem: str,
    quiz_size_preference: Optional[str] = None
):
    asyncio.run(generate_and_save_quiz_task(
        source_material,
        requested_quiz_title,
        custom_quiz_filepath,
        temp_pdf_path,
        quiz_id_stem,
        quiz_size_preference
    ))

# --- Worker Thread Function ---
def quiz_generation_worker(q: queue.Queue):
    print("Quiz generation worker thread started.")
    while True:
        try:
            task_data = q.get(block=True, timeout=0.5) # block with timeout to allow periodic checks if needed
            if task_data is WORKER_SENTINEL:
                print("Worker thread: Sentinel received. Exiting.")
                q.task_done()
                break

            task_type = task_data.get("task_type")
            quiz_id_stem_log = task_data.get('quiz_id_stem', 'N/A_QUIZ_ID') # For logging
            session_id_log = task_data.get('session_id', 'N/A_SESSION_ID') # For logging

            if task_type == "generate_quiz":
                print(f"Worker thread: Got 'generate_quiz' task for quiz_id_stem: {quiz_id_stem_log}")
                try:
                    run_generate_and_save_quiz_task_sync(
                        source_material=task_data["source_material"],
                        requested_quiz_title=task_data["requested_quiz_title"],
                        custom_quiz_filepath=task_data["custom_quiz_filepath"],
                        temp_pdf_path=task_data["temp_pdf_path"],
                        quiz_id_stem=task_data["quiz_id_stem"],
                        quiz_size_preference=task_data["quiz_size_preference"]
                    )
                except Exception as e_task:
                    print(f"Worker thread: Error processing 'generate_quiz' task for {quiz_id_stem_log}: {type(e_task).__name__} - {e_task}")
            
            elif task_type == "initialize_tutor":
                session_id = task_data["session_id"]
                quiz_instance_key = task_data["quiz_instance_key"]
                print(f"Worker thread: Got 'initialize_tutor' task for session {session_id}, quiz {quiz_instance_key}")
                try:
                    session_data_for_tutor = active_sessions.get(session_id)
                    if not session_data_for_tutor:
                        print(f"Worker: Session {session_id} not found in active_sessions for tutor init.")
                        active_sessions[session_id] = get_session_data(session_id) # Initialize if somehow missed
                        active_sessions[session_id]["tutor_init_failed"] = True
                        q.task_done()
                        continue

                    # Ensure user_quizzes exists
                    if "user_quizzes" not in session_data_for_tutor:
                         session_data_for_tutor["user_quizzes"] = {}
                    
                    user_quizzes = session_data_for_tutor.get("user_quizzes")
                    quiz_to_init_tutor_for = user_quizzes.get(quiz_instance_key) # This should be the Quiz object
                                        
                    if not quiz_to_init_tutor_for:
                        # Attempt to load it if it's the current_quiz_instance, maybe it wasn't in user_quizzes yet
                        # This case might be rare if start-quiz logic is robust
                        if session_data_for_tutor.get("current_quiz_instance_key") == quiz_instance_key and \
                           session_data_for_tutor.get("current_quiz_instance"):
                            quiz_to_init_tutor_for = session_data_for_tutor["current_quiz_instance"]
                            print(f"Worker: Tutor init for {quiz_instance_key} (session {session_id}) - using current_quiz_instance as fallback.")
                        else:
                            print(f"Worker: Quiz {quiz_instance_key} not found in user_quizzes or current_quiz_instance for session {session_id} for tutor init.")
                            session_data_for_tutor["tutor_init_failed"] = True
                            q.task_done()
                            continue
                    
                    if not hasattr(quiz_to_init_tutor_for, 'get_tutor') or not callable(getattr(quiz_to_init_tutor_for, 'get_tutor')):
                        print(f"Worker: Quiz object for {quiz_instance_key} (session {session_id}) does not have a get_tutor method.")
                        session_data_for_tutor["tutor_init_failed"] = True
                        q.task_done()
                        continue

                    # Ensure message_queue is a list
                    if "message_queue" not in session_data_for_tutor or not isinstance(session_data_for_tutor["message_queue"], list):
                        session_data_for_tutor["message_queue"] = []
                    
                    print(f"Worker: Attempting to call get_tutor for quiz {quiz_instance_key} (session {session_id}).")
                    initialized_tutor = quiz_to_init_tutor_for.get_tutor(
                        session_message_queue_ref=session_data_for_tutor["message_queue"]
                    )
                    session_data_for_tutor["current_tutor_instance"] = initialized_tutor
                    session_data_for_tutor["tutor_initialized_by_worker"] = True
                    session_data_for_tutor["tutor_init_failed"] = False # Reset on success
                    print(f"Worker thread: Tutor initialized successfully for session {session_id}, quiz {quiz_instance_key}. Type: {type(initialized_tutor)}")

                except Exception as e_tutor_init:
                    print(f"Worker thread: Error initializing tutor for session {session_id}, quiz {quiz_instance_key}: {type(e_tutor_init).__name__} - {e_tutor_init}")
                    # Ensure session_data_for_tutor exists before trying to set a flag on it
                    if session_id in active_sessions and active_sessions.get(session_id):
                        active_sessions[session_id]["tutor_init_failed"] = True
                    else: # If session_data itself couldn't be retrieved, this is a more fundamental issue
                        print(f"Worker thread: CRITICAL - Could not access session data for {session_id} during tutor init exception handling.")
            else:
                print(f"Worker thread: Unknown task type '{task_type}' received for quiz {quiz_id_stem_log} / session {session_id_log}")
            
            q.task_done()
        except queue.Empty:
            continue # Loop again, effectively sleeping due to q.get timeout
        except Exception as e:
            print(f"Worker thread: Critical error in main loop: {type(e).__name__} - {e}")
            time.sleep(1) # Avoid rapid spinning on unexpected errors
    print("Quiz generation worker thread finished.")


worker_thread = Thread(target=quiz_generation_worker, args=(task_queue,), daemon=True)

@app.on_event("startup")
async def startup_event():
    print("Application startup: Starting quiz generation worker thread...")
    if not worker_thread.is_alive():
        worker_thread.start()
        print("Quiz generation worker thread started.")
    else:
        print("Quiz generation worker thread already alive.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown: Signaling worker thread to stop...")
    task_queue.put(WORKER_SENTINEL) # Signal the worker to exit
    worker_thread.join(timeout=5) # Wait for the worker thread to finish
    if worker_thread.is_alive():
        print("Worker thread did not shut down gracefully.")
    else:
        print("Quiz generation worker thread shut down.")


@app.post("/api/initiate-quiz-generation", response_class=JSONResponse)
async def initiate_quiz_generation(
    request: Request,
    file: UploadFile = File(...),
    quiz_title_form: Optional[str] = Form(None),
    quiz_size_preference: Optional[str] = Form(None)
):
    """Initiates PDF processing and AI quiz generation by adding a task to the queue.
    Custom quiz files will be named {session_id}_custom_{uuid}.json.
    If quiz_title_form is not provided, title generation will be attempted in the background.
    """
    session_id = get_session_id(request)

    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type or missing filename. Only PDF is supported.")

    # uploads_dir = Path(__file__).parent / "uploads" # Old path
    # UPLOADS_DIR is now defined globally
    # UPLOADS_DIR.mkdir(parents=True, exist_ok=True) # ensure_directory_exists handles this
    
    sane_filename = "".join(c for c in Path(file.filename).name if c.isalnum() or c in ['.', '_', '-']).strip()
    if not sane_filename: 
        sane_filename = "uploaded_document.pdf"

    temp_pdf_filename = f"{session_id}_{uuid.uuid4().hex[:8]}_{sane_filename}"
    temp_pdf_path = UPLOADS_DIR / temp_pdf_filename # Use new UPLOADS_DIR

    title_for_generation_task = quiz_title_form.strip() if quiz_title_form and quiz_title_form.strip() else ""
    user_specific_quiz_id_stem = f"{session_id}_custom_{uuid.uuid4().hex[:8]}"
    custom_quiz_filepath = DATA_DIR / f"{user_specific_quiz_id_stem}.json" # DATA_DIR is new global
    
    display_title_immediate = title_for_generation_task if title_for_generation_task else f"Quiz from: {sane_filename[:30]}"
    if len(display_title_immediate) > 60: display_title_immediate = display_title_immediate[:57] + "..."

    try:
        with open(temp_pdf_path, "wb") as buffer:
            buffer.write(await file.read())
        print(f"PDF '{sane_filename}' saved to '{temp_pdf_path}' for quiz ID '{user_specific_quiz_id_stem}' (session: {session_id})")

        source_material = qc.openpdf(str(temp_pdf_path))
        if not source_material or not source_material.strip():
            if temp_pdf_path.exists(): temp_pdf_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Could not extract text from PDF, or PDF is empty/unreadable.")

        # Prepare task data
        task_data = {
            "task_type": "generate_quiz", # Specify task type
            "source_material": source_material,
            "requested_quiz_title": title_for_generation_task,
            "custom_quiz_filepath": custom_quiz_filepath,
            "temp_pdf_path": temp_pdf_path,
            "quiz_id_stem": user_specific_quiz_id_stem,
            "quiz_size_preference": quiz_size_preference,
            "session_id": session_id # For logging/context if needed by quiz gen
        }

        # Put the task onto the global queue
        task_queue.put(task_data)
        
        print(f"Quiz generation task for ID '{user_specific_quiz_id_stem}' (initial title: '{title_for_generation_task if title_for_generation_task else '[Auto-generate]'}', size_pref: {quiz_size_preference or 'auto'}) added to the queue.")
        
        return JSONResponse({
            "status": "generating",
            "quiz_id": user_specific_quiz_id_stem, 
            "quiz_title": display_title_immediate,
            "message": "Quiz generation task queued. It will appear on the main page when ready."
        })

    except HTTPException as http_exc:
        if temp_pdf_path.exists(): temp_pdf_path.unlink(missing_ok=True)
        raise http_exc
    except Exception as e:
        if temp_pdf_path.exists(): temp_pdf_path.unlink(missing_ok=True)
        print(f"Error during synchronous part of PDF processing for quiz ID '{user_specific_quiz_id_stem}': {type(e).__name__} - {e}")
        raise HTTPException(status_code=500, detail=f"Server error processing PDF ({sane_filename}). Please try again or use a different file.")

@app.post("/api/chat-with-tutor", response_class=JSONResponse)
async def chat_with_tutor_api(request: Request, message_data: Dict[str, str]):
    """Handles follow-up chat messages with the tutor."""
    session_id = get_session_id(request)
    user_message = message_data.get("message")

    if not user_message:
        raise HTTPException(status_code=400, detail="Message not provided.")

    tutor = get_current_tutor_instance(session_id)
    if not tutor:
        raise HTTPException(status_code=404, detail="Active tutor session not found.")

    # Check if there's an active question
    q_details = get_session_data(session_id)["current_question_details"]
    if not q_details:
        raise HTTPException(status_code=400, detail="No active question found. Please answer a question first.")

    ai_messages_for_user = get_tutor_message_queue(session_id)
    ai_messages_for_user.clear()  # Clear previous messages before new interaction

    try:
        tutor.prompt(f"User follow-up: {user_message}")
    except Exception as e:
        print(f"Error during tutor chat: {e}")
        ai_messages_for_user.append(f"Sorry, I encountered an issue: {e}")
        return JSONResponse({"ai_messages": list(ai_messages_for_user)}, status_code=500)

    return JSONResponse({"ai_messages": list(ai_messages_for_user)})


@app.post("/api/tts", response_class=JSONResponse)
async def text_to_speech_api(request: Request, text_data: Dict[str, str]):
    """Generates speech from text using Google Cloud TTS premium voices."""
    from fastapi.responses import StreamingResponse
    import io
    import google_tts


    text_to_speak = text_data.get("text")
    if not text_to_speak:
        print("TTS Error: No text provided")
        raise HTTPException(status_code=400, detail="No text provided for TTS.")

    try:
        # Use the premium TTS function from google_tts.py
        audio_content = google_tts.text_to_speech_premium(text_to_speak)

        # Return the audio content as a streaming response
        return StreamingResponse(io.BytesIO(audio_content), media_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

@app.post("/api/delete-quiz/{quiz_name_id_to_delete}", response_class=JSONResponse)
async def delete_custom_quiz(request: Request, quiz_name_id_to_delete: str):
    session_id = get_session_id(request)
    session_data = get_session_data(session_id)

    # Security Check: Ensure the quiz_name_id starts with the session_id and "_custom_"
    # This confirms the user owns this quiz and it is a custom quiz.
    if not quiz_name_id_to_delete.startswith(f"{session_id}_custom_"):
        print(f"Attempt to delete non-custom or unauthorized quiz: {quiz_name_id_to_delete} by session {session_id}")
        raise HTTPException(status_code=403, detail="You can only delete your own custom quizzes.")

    quiz_file_path = DATA_DIR / f"{quiz_name_id_to_delete}.json"

    if not quiz_file_path.exists() or not quiz_file_path.is_file():
        print(f"Custom quiz file not found for deletion: {quiz_file_path}")
        raise HTTPException(status_code=404, detail=f"Custom quiz '{quiz_name_id_to_delete}' not found.")

    try:
        quiz_file_path.unlink() # Delete the JSON file
        print(f"Successfully deleted quiz file: {quiz_file_path}")

        # Remove from active session data if present
        if quiz_name_id_to_delete in session_data.get("user_quizzes", {}):
            del session_data["user_quizzes"][quiz_name_id_to_delete]
            print(f"Removed quiz '{quiz_name_id_to_delete}' from active session '{session_id}'.")
        
        # If the deleted quiz was the current active quiz, clear it from session
        if session_data.get("current_quiz_instance_key") == quiz_name_id_to_delete:
            session_data["current_quiz_instance_key"] = None
            session_data["current_quiz_instance"] = None
            session_data["current_tutor_instance"] = None
            session_data["current_question_details"] = None
            session_data["current_score"] = {"correct": 0, "total": 0}
            request.session.pop("current_quiz_name", None)
            request.session.pop("current_quiz_title", None)
            print(f"Cleared active quiz session for deleted quiz '{quiz_name_id_to_delete}'.")

        return {"status": "success", "message": f"Quiz '{quiz_name_id_to_delete}' deleted successfully."}
    except Exception as e:
        print(f"Error deleting quiz '{quiz_name_id_to_delete}': {e}")
        raise HTTPException(status_code=500, detail=f"Could not delete quiz '{quiz_name_id_to_delete}'. An error occurred.")

@app.post("/api/rename-quiz/{quiz_name_id_to_rename}", response_class=JSONResponse)
async def rename_custom_quiz(request: Request, quiz_name_id_to_rename: str, payload: Dict[str, str]):
    session_id = get_session_id(request)
    session_data = get_session_data(session_id)
    new_title = payload.get("new_title")

    if not new_title or not new_title.strip():
        raise HTTPException(status_code=400, detail="New title cannot be empty.")
    
    new_title = new_title.strip()

    if not quiz_name_id_to_rename.startswith(f"{session_id}_custom_"):
        print(f"Attempt to rename non-custom or unauthorized quiz: {quiz_name_id_to_rename} by session {session_id}")
        raise HTTPException(status_code=403, detail="You can only rename your own custom quizzes.")

    quiz_file_path = DATA_DIR / f"{quiz_name_id_to_rename}.json"

    if not quiz_file_path.exists() or not quiz_file_path.is_file():
        print(f"Custom quiz file not found for renaming: {quiz_file_path}")
        raise HTTPException(status_code=404, detail=f"Custom quiz '{quiz_name_id_to_rename}' not found.")

    try:
        # Load the quiz data from JSON file
        with open(quiz_file_path, 'r') as f:
            quiz_data_dict = json.load(f)
        
        original_title = quiz_data_dict.get("title", "Untitled")
        quiz_data_dict["title"] = new_title # Update the title

        # Save the modified quiz data back to the JSON file
        with open(quiz_file_path, 'w') as f:
            json.dump(quiz_data_dict, f, indent=4)
        print(f"Successfully renamed quiz file '{quiz_file_path}' from '{original_title}' to '{new_title}'")

        # Update in active session data if present
        if quiz_name_id_to_rename in session_data.get("user_quizzes", {}):
            quiz_instance = session_data["user_quizzes"].get(quiz_name_id_to_rename)
            if quiz_instance and hasattr(quiz_instance, 'title'):
                quiz_instance.title = new_title
                print(f"Updated title in active session for quiz '{quiz_name_id_to_rename}'.")
        
        # If the renamed quiz was the current active quiz, update its title in Starlette session
        if session_data.get("current_quiz_instance_key") == quiz_name_id_to_rename:
            request.session["current_quiz_title"] = new_title
            print(f"Updated current_quiz_title in Starlette session for '{quiz_name_id_to_rename}'.")

        return {"status": "success", "message": f"Quiz '{original_title}' renamed to '{new_title}' successfully.", "new_title": new_title}
    except json.JSONDecodeError:
        print(f"Error decoding JSON for quiz '{quiz_name_id_to_rename}' during rename.")
        raise HTTPException(status_code=500, detail="Error reading quiz data for renaming.")
    except Exception as e:
        print(f"Error renaming quiz '{quiz_name_id_to_rename}': {e}")
        raise HTTPException(status_code=500, detail=f"Could not rename quiz '{quiz_name_id_to_rename}'. An error occurred.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
