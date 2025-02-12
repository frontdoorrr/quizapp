"""Email utility class"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "geniusgamekorea@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "kfzk hpsl dhmb ethd")
        self.sender_email = os.getenv("SENDER_EMAIL", "geniusgamekorea@gmail.com")

    def send_verification_email(self, to_email: str, verification_token: str):
        """Send verification email

        Args:
            to_email (str): Recipient email
            verification_token (str): Verification token
        """
        verification_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = to_email
        msg["Subject"] = "[Genius Game] 이메일 인증번호"

        html_content = f"""
        <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body style="font-family: sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #333;">이메일 인증번호</h2>
                    <p style="color: #666;">아래의 인증번호를 입력하여 이메일 인증을 완료해주세요:</p>
                    <div style="background-color: #f5f5f5;
                                padding: 20px;
                                border-radius: 5px;
                                margin: 20px 0;
                                text-align: center;
                                font-size: 24px;
                                letter-spacing: 5px;
                                font-weight: bold;
                                color: #333;">
                        {verification_token}
                    </div>
                    <p style="color: #666; font-size: 14px;">* 이 인증번호는 3분 동안만 유효합니다.</p>
                </div>
            </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # try:
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
        # except Exception as e:
        # raise Exception(f"Failed to send email: {str(e)}")
