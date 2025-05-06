
from pydantic import BaseModel, field_validator
from typing import Optional, Dict


class Student(BaseModel):
    name: str
    age: int
    class_level: int
    subjects: Dict[str, int]
    address: Optional[str] = None

    @field_validator('subjects')
    @classmethod
    def validate_subjects(cls, value):
        for subject, marks in value.items():
            if not (0 <= marks <= 100):
                raise ValueError(f"Marks for {subject} must be between 0 and 100")
        return value
    
    def average(self) -> float:
        """Calculate the average marks of the student."""
        return sum(self.subjects.values()) / len(self.subjects) if self.subjects else 0.0
    
    def grade(self) -> str:
        """Determine the grade based on average marks."""
        avg = self.average()
        if avg >= 90:
            return 'A'
        elif avg >= 80:
            return 'B'
        elif avg >= 70:
            return 'C'
        elif avg >= 60:
            return 'D'
        else:
            return 'F'
    