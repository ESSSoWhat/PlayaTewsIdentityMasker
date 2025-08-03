import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import List, Union


def _validate_args(args: List[str]) -> bool:
    """Validate and sanitize command line arguments"""
    if not isinstance(args, list):
        return False

    # Check for potentially dangerous patterns
    dangerous_patterns = [";", "&", "|", "`", "$", "(", ")", "<", ">"]
    for arg in args:
        if not isinstance(arg, str):
            return False
        for pattern in dangerous_patterns:
            if pattern in arg:
                return False

    return True


def _validate_filename(filename: str) -> bool:
    """Validate filename for security"""
    if not isinstance(filename, str):
        return False

    # Check for path traversal attempts
    dangerous_patterns = ["..", "~", "/etc", "/var", "/proc", "/sys"]
    filename_lower = filename.lower()
    for pattern in dangerous_patterns:
        if pattern in filename_lower:
            return False

    # Ensure it's a valid file path
    try:
        path = Path(filename)
        return path.is_file() or path.parent.exists()
    except Exception:
        return False


def run(
    args, pipe_stdin=False, pipe_stdout=False, pipe_stderr=False, quiet_stderr=False
) -> Union[subprocess.Popen, None]:
    """
    run ffmpeg process with security validation

    returns Popen class if success
    otherwise None
    """
    # Validate input arguments
    if not _validate_args(args):
        print("ffmpeg error: Invalid arguments provided")
        return None

    # Build command list safely
    cmd = ["ffmpeg"] + args

    stdin_stream = subprocess.PIPE if pipe_stdin else None
    stdout_stream = subprocess.PIPE if pipe_stdout else None
    stderr_stream = subprocess.PIPE if pipe_stderr else None

    if quiet_stderr and not pipe_stderr:
        stderr_stream = subprocess.DEVNULL

    try:
        # Use shell=False for security
        return subprocess.Popen(
            cmd,
            stdin=stdin_stream,
            stdout=stdout_stream,
            stderr=stderr_stream,
            shell=False,
        )
    except Exception as e:
        print("ffmpeg exception: ", e)
    return None


def probe(filename):
    """Run ffprobe on the specified file and return a JSON representation of the output.

    Raises:
        Exception if ffprobe returns a non-zero exit code,
    """
    # Validate filename
    if not _validate_filename(filename):
        raise ValueError(f"Invalid or unsafe filename: {filename}")

    args = ["ffprobe", "-show_format", "-show_streams", "-of", "json", filename]

    try:
        # Use shell=False for security
        p = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False
        )
        out, err = p.communicate()
        if p.returncode != 0:
            raise Exception("ffprobe", out, err)
        return json.loads(out.decode("utf-8"))
    except subprocess.SubprocessError as e:
        raise Exception(f"ffprobe subprocess error: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"ffprobe JSON decode error: {e}")
    except Exception as e:
        raise Exception(f"ffprobe error: {e}")
