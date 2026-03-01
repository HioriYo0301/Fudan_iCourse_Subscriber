"""Email notification via QQ SMTP."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from . import config


def _md_to_html(md_text: str) -> str:
    """Convert Markdown to HTML, falling back to <pre> on error."""
    try:
        import markdown

        return markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    except ImportError:
        return f"<pre>{md_text}</pre>"


class Emailer:
    """Send course summary emails via QQ SMTP SSL."""

    def __init__(self):
        self.host = config.SMTP_HOST
        self.port = config.SMTP_PORT
        self.sender = config.SMTP_EMAIL
        self.password = config.SMTP_PASSWORD
        self.receiver = config.RECEIVER_EMAIL

    def send(
        self,
        course_title: str,
        sub_title: str,
        date: str,
        summary: str,
    ):
        """Send an email with the lecture summary.

        Args:
            course_title: Name of the course.
            sub_title: Lecture title.
            date: Lecture date string.
            summary: Markdown-formatted summary.
        """
        subject = f"[iCourse] {course_title} - {sub_title} ({date})"

        plain = f"课程：{course_title}\n课次：{sub_title}\n日期：{date}\n\n{summary}"
        html_body = _md_to_html(summary)
        html = (
            f"<h2>{course_title}</h2>"
            f"<p><b>课次：</b>{sub_title} &nbsp; <b>日期：</b>{date}</p>"
            f"<hr>{html_body}"
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = self.receiver
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL(self.host, self.port) as server:
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receiver, msg.as_string())

        print(f"[Emailer] Sent: {subject}")
