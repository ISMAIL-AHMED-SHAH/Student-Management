import json
from pathlib import Path
from models.student import Student
from typing import List

DATA_FILE = Path("students.json")

def load_students() -> List[Student]:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return [Student(**item) for item in data]
    return []

def save_students(students: List[Student]) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump([student.model_dump() for student in students], f, indent=4)
