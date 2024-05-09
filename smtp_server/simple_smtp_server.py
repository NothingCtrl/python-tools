import traceback
import time
import sys
import os
from datetime import datetime
import asyncore
from smtpd import SMTPServer
import smtplib, ssl
from dotenv import load_dotenv

load_dotenv()


def send_email(receiver: list, message: str, sender_email: str, sender_pw: str, smtp_server: str, smtp_port: int = 587):
    if os.getenv('DEBUG', '0') == '1':
        print("=== [DEBUG] send_email ===")
        print(f"receiver: {receiver}")
        print(f"message: {message}")
        print(f"sender_email: {sender_email}")
        print(f"sender_pw: {sender_pw}")
        print(f"smtp_server: {smtp_server}")
        print(f"smtp_port: {smtp_port}")
        print("=== END ===")
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, sender_pw)
            server.ehlo()
            server.sendmail(sender_email, receiver, message)
            server.quit()
    except Exception:
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        with open(f"logs/error_log_{int(time.time())}.txt", "w+") as f:
            f.write(f"""=== ERROR ===
receiver: {receiver}
message: {message}

----- traceback -----
{traceback.format_exc()}
            """)


class EmlServer(SMTPServer):
    no = 0

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):

        sender_email = os.getenv("SENDER_EMAIL", "")
        sender_pw = os.getenv("SENDER_PW", "")
        smtp_server = os.getenv("SMTP_SERVER", "")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        if sender_email and sender_pw and smtp_server:
            send_email(rcpttos, data, sender_email, sender_pw, smtp_server, smtp_port)
        else:
            filename = '%s-%d.eml' % (datetime.now().strftime('%Y%m%d%H%M%S'),
                                      self.no)
            print("-" * 80)
            print(f"mailfrom: {mailfrom}")
            print(f"rcpttos: {rcpttos}")
            print(f"data: {data}")
            print(f"kwargs: {kwargs}")
            print("*" * 30)
            print(filename)
            f = open(filename, 'wb')
            f.write(data)
            f.close
            print('%s saved.' % filename)
            print("*" * 80)
            self.no += 1


def run():
    EmlServer(('localhost', 25), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) == 3 and sys.argv[1] == 'smtp-test' and '@' in sys.argv[2]:
            _sender_email = os.getenv("SENDER_EMAIL", "")
            _sender_pw = os.getenv("SENDER_PW", "")
            _smtp_server = os.getenv("SMTP_SERVER", "")
            _smtp_port = int(os.getenv("SMTP_PORT", "587"))
            _receivers = [sys.argv[2]]
            if _sender_email and _sender_pw and _smtp_server:
                os.environ['DEBUG'] = '1'
                _message = f"""Subject: Test message subject\nTo: {', '.join(_receivers)}\n
                
                This is a test message."""
                send_email(_receivers, _message, _sender_email, _sender_pw, _smtp_server, _smtp_port)
            else:
                print("[ERROR] missing required configs value")
        else:
            print("[ERROR] invalid params!")
    else:
        run()
