from pydantic import BaseModel

# 1. Define the nested Telemetry object
class TelemetryData(BaseModel):
    clicked_diagram: bool
    read_summary_first: bool
    time_spent_on_text: int
    time_spent_on_visuals: int
    time_spent_on_summary: int
    scrolled_erratically: bool

# 2. Define the nested Quiz object
class QuizResultsData(BaseModel):
    score: int
    q1_correct: bool
    q2_correct: bool
    q3_correct: bool

# 3. Combine them into the main payload FastAPI will expect
class CalibrationPayload(BaseModel):
    telemetry: TelemetryData
    quiz_results: QuizResultsData