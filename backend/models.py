import uuid
from datetime import datetime


class Session:
    def __init__(self, candidate_name, job_title):
        self.session_id = str(uuid.uuid4())
        self.candidate_name = candidate_name
        self.job_title = job_title
        self.start_time = datetime.now().isoformat()
        self.end_time = None
        self.answers = []
        self.scorecard = None

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "candidate_name": self.candidate_name,
            "job_title": self.job_title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "answers": self.answers,
            "scorecard": self.scorecard,
        }