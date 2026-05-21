"""
邮件通知模块
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional
from pathlib import Path
from src.config import config
from src.logger import logger


class EmailSendError(Exception):
    pass


class EmailNotifier:
    """邮件通知类"""

    SMTP_HOST = "smtp.qq.com"
    SMTP_PORT = 465

    def __init__(
        self,
        sender_email: str,
        auth_code: str,
        receiver_emails: List[str]
    ):
        self.sender_email = sender_email
        self.auth_code = auth_code
        self.receiver_emails = receiver_emails

    def send(
        self,
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[str]] = None
    ) -> None:
        """
        发送邮件，失败时抛出 EmailSendError

        Args:
            subject: 邮件主题
            body: 邮件正文
            is_html: 是否为HTML格式
            attachments: 附件路径列表
        """
        try:
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = ", ".join(self.receiver_emails)
            message["Subject"] = subject

            msg_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, msg_type, "utf-8"))

            if attachments:
                self._add_attachments(message, attachments)

            with smtplib.SMTP_SSL(self.SMTP_HOST, self.SMTP_PORT) as server:
                server.login(self.sender_email, self.auth_code)
                server.sendmail(
                    self.sender_email,
                    self.receiver_emails,
                    message.as_string()
                )

            logger.info(f"邮件发送成功: {self.receiver_emails}")

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            raise EmailSendError(f"邮件发送失败: {e}") from e

    def _add_attachments(self, message: MIMEMultipart, attachments: List[str]) -> None:
        for file_path in attachments:
            try:
                path = Path(file_path)
                if not path.exists():
                    logger.warning(f"附件不存在: {file_path}")
                    continue
                with open(path, "rb") as file:
                    part = MIMEApplication(file.read(), Name=path.name)
                part['Content-Disposition'] = f'attachment; filename="{path.name}"'
                message.attach(part)
                logger.debug(f"添加附件: {file_path}")
            except Exception as e:
                logger.error(f"无法添加附件 {file_path}: {e}")


def create_notifier() -> Optional[EmailNotifier]:
    if not config.QQ_EMAIL or not config.QQ_AUTH_CODE:
        logger.error("邮箱配置不完整，请检查.env文件")
        return None
    if not config.RECEIVER_EMAILS:
        logger.error("收件人列表为空，请检查.env文件")
        return None
    return EmailNotifier(
        sender_email=config.QQ_EMAIL,
        auth_code=config.QQ_AUTH_CODE,
        receiver_emails=config.RECEIVER_EMAILS
    )
