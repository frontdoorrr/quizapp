"""Email utility class"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import datetime


class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "geniusgamekorea@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "kfzk hpsl dhmb ethd")
        self.sender_email = os.getenv("SENDER_EMAIL", "geniusgamekorea@gmail.com")

    def send_email(self, to_email: str, subject: str, content: str, is_html: bool = False):
        """Send general email

        Args:
            to_email (str): Recipient email
            subject (str): Email subject
            content (str): Email content
            is_html (bool): Whether the content is HTML
        """
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = to_email
        msg["Subject"] = Header(subject, "utf-8")

        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(content, content_type, "utf-8"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)

    def send_verification_email(self, to_email: str, verification_token: str):
        """Send verification email

        Args:
            to_email (str): Recipient email
            verification_token (str): Verification token
        """
        verification_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={verification_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>이메일 인증</title>
            <style>
                body {{
                    font-family: 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f9f9f9;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 1px solid #eee;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #4A6FFF;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                h1 {{
                    color: #333;
                    font-size: 22px;
                    margin-top: 0;
                }}
                p {{
                    margin-bottom: 20px;
                }}
                .verification-code {{
                    background-color: #f5f5f5;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    text-align: center;
                    font-size: 28px;
                    letter-spacing: 5px;
                    font-weight: bold;
                    color: #333;
                }}
                .footer {{
                    text-align: center;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #999;
                }}
                .note {{
                    font-size: 13px;
                    color: #888;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Genius Game</div>
                </div>
                <div class="content">
                    <h1>이메일 인증</h1>
                    <p>안녕하세요,</p>
                    <p>Genius Game에 가입해 주셔서 감사합니다. 아래의 인증번호를 입력하여 이메일 인증을 완료해주세요.</p>
                    <div class="verification-code">
                        {verification_token}
                    </div>
                    <p class="note">* 이 인증번호는 3분 동안만 유효합니다.</p>
                    <p>인증번호 입력이 어려우신 경우, 아래 링크를 클릭하여 인증을 완료하실 수도 있습니다:</p>
                    <p style="word-break: break-all; font-size: 13px; color: #666;"><a href="{verification_link}">{verification_link}</a></p>
                </div>
                <div class="footer">
                    <p>&copy; {datetime.datetime.now().year} Genius Game. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = to_email
        msg["Subject"] = Header("[Genius Game] 이메일 인증", "utf-8")

        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
