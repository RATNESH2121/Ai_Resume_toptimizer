from django.db import models


class ResumeSession(models.Model):
    """Stores a resume analysis session."""
    session_id = models.CharField(max_length=64, unique=True)
    jd_text = models.TextField(blank=True)
    resume_text = models.TextField(blank=True)
    ats_score = models.FloatField(null=True, blank=True)
    match_percent = models.IntegerField(null=True, blank=True)
    feedback_json = models.JSONField(null=True, blank=True)
    optimized_resume_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session {self.session_id} | Score: {self.ats_score}"
