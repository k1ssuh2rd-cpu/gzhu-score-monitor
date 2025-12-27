"""
SMTP连接测试脚本
"""
import smtplib
import ssl
from src.config import config

def test_smtp_connection():
    """测试SMTP连接"""
    print("=" * 60)
    print("SMTP连接测试")
    print("=" * 60)
    print(f"SMTP服务器: {config.QQ_EMAIL.split('@')[1]}")
    print(f"SMTP主机: smtp.qq.com")
    print(f"SMTP端口: 465 (SSL)")
    print(f"发送邮箱: {config.QQ_EMAIL}")
    print(f"授权码: {config.QQ_AUTH_CODE[:4]}...{config.QQ_AUTH_CODE[-4:]}")
    print(f"测试收件人: {config.TEST_EMAIL}")
    print()
    
    try:
        print("尝试连接SMTP服务器...")
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL("smtp.qq.com", 465, context=context) as server:
            server.set_debuglevel(1)  # 启用调试模式
            print("✓ SSL连接成功")
            
            print("尝试登录...")
            server.login(config.QQ_EMAIL, config.QQ_AUTH_CODE)
            print("✓ 登录成功")
            
            print("尝试发送测试邮件...")
            from email.mime.text import MIMEText
            msg = MIMEText("这是一封测试邮件", "plain", "utf-8")
            msg["From"] = config.QQ_EMAIL
            msg["To"] = config.TEST_EMAIL
            msg["Subject"] = "SMTP连接测试"
            
            try:
                result = server.sendmail(config.QQ_EMAIL, config.TEST_EMAIL, msg.as_string())
                print(f"✓ 邮件发送成功: {result}")
            except smtplib.SMTPRecipientsRefused as e:
                print(f"✗ 收件人被拒绝: {e}")
                print(f"拒绝的收件人: {e.recipients}")
                return False
            except smtplib.SMTPDataError as e:
                print(f"✗ 数据错误: {e}")
                return False
            
        print()
        print("=" * 60)
        print("SMTP连接测试完成！")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ 认证失败: {e}")
        print("请检查授权码是否正确")
        return False
        
    except smtplib.SMTPException as e:
        print(f"✗ SMTP错误: {e}")
        return False
        
    except Exception as e:
        print(f"✗ 连接错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_smtp_connection()
