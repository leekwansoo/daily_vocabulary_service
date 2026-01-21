"""
mailer.py

Scans `mailed.json` and emails the words whose `mailed_date` equals today's date.

Usage examples:
  # Dry run (prints email content but does not send)
  python mailer.py --dry-run

  # Send using environment variables for SMTP credentials and recipient
  set SMTP_SERVER=smtp.example.com
  set SMTP_PORT=587
  set SMTP_USER=you@example.com
  set SMTP_PASS=yourpassword
  set MAIL_FROM=you@example.com
  set MAIL_TO=recipient@example.com
  python mailer.py

Scheduling:
  - Windows: create a Task Scheduler task to run this script daily at 23:59
  - Linux/macOS: add a cron job to run daily at 23:59

Notes:
  - The script expects `mailed.json` to be in the current working directory or in the project root.
  - SMTP credentials may require app-specific passwords for providers like Gmail.
"""

import os
import json
import argparse
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
from utils.json_manager import load_mailed_words
from database.subscriber_db import list_subscribers
from dotenv import load_dotenv
load_dotenv()

# Get the env variables for SMTP server configuration
MAIL_FROM = "leekwansoo49@gmail.com"
MAIL_TO = []
# get subscriber list from subscriber manager
subscribers = list_subscribers()
print("Loaded subscribers:", subscribers)
for sub in subscribers:
    # print("Subscriber email:", sub.email, "level:", sub.level)
    if sub.email not in MAIL_TO:
        MAIL_TO.append(sub.email)
        
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT', 587))
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASSWORD')
from_addr = MAIL_FROM
to_addr = MAIL_TO  # List of recipients


def get_today_iso_date():
    # Use local date for comparison (strip time)
    return datetime.now().date().isoformat()


def build_email_content(words):
    # Build plain text and simple HTML
    lines = []
    html_lines = ["<html><body>", "<h2>Today's Mailed Words</h2>", "<ul>"]

    for w in words:
        print("Processing word for email content:", w)
        word = w.get('word', '')
        meaning = w.get('meaning', '')
        phrase = w.get('phrase', '')
        media = w.get('media', '')
        
        
        lines.append(f"- {word} | {meaning} | {phrase} | {media}")
        html_lines.append(f"<li><strong>{word}</strong> &mdash; {meaning}<br/><em>{phrase}</em><br/><em>{media}</em></li>")

    html_lines.append("</ul>")
    html_lines.append("</body></html>")

    plain = "\n".join(lines)
    html = "\n".join(html_lines)
    return plain, html


def send_email(smtp_server, smtp_port, smtp_user, smtp_pass, from_addr, to_addr, subject, plain, html):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")

    # Connect and send
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        if smtp_user and smtp_pass:
            smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)


async def mail_trigger(words=None, to_addr = None):
    if to_addr is None:
        to_addr = MAIL_TO
    # 
    today = get_today_iso_date()
    (print(f"Today's date: {today}"))
    if words is not None:
        print(f"Mail trigger called for words: {words}")
        mailed_words = words
    else:
        mailed_words = load_mailed_words()
    # print(f"mailed: {mailed_words}")
    if not mailed_words:
        # print("No mailed words found.")
        return {'status': 'no_mailed_words'}

    # Filter words whose mailed_date date portion equals today
    print(f"mailed_words: {mailed_words}")
    matches = []
    # print(f"mailed: {mailed_words}")
    for w in mailed_words:
        md = w.get('mailed_date') or w.get('date') or ''
        print("mailed_date field:", repr(md))
        if not md:
            continue
        try:
            # Parse ISO-like datetime and compare date portion
            parsed = datetime.fromisoformat(md)
            dt_date = parsed.date().isoformat()
        except Exception:
            # If parsing fails, try taking leading 10 chars
            dt_date = md[:10]

        if dt_date == today:
            matches.append(w)

    if not matches:
        print(f"No mailed words with mailed_date == {today}.")
        return {'status': 'no_matching_mailed_words'}

    subject = f"Mailed words for {today}"
    plain, html = build_email_content(matches)

        # Validate SMTP config
    
    if not smtp_server or not from_addr or not to_addr:
        print("Missing SMTP_SERVER, MAIL_FROM, or MAIL_TO configuration. Use environment variables or CLI args.")
        return

    try:
        send_email(smtp_server, smtp_port, smtp_user, smtp_pass, from_addr, to_addr, subject, plain, html)
        print("Email sent successfully to", to_addr)

        # Mark entries as sent unless user disabled marking
        # if not args.no_mark:
        mailed_file = os.path.join(os.getcwd(), "mailed.json")
        try:
            if os.path.exists(mailed_file):
                with open(mailed_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            else:
                existing = []

            now_iso = datetime.now().isoformat()
            # Update matching entries by matching word and mailed_date (date portion)
            updated = []
            for item in existing:
                item_md = item.get('mailed_date') or item.get('date') or ''
                item_date = ''
                try:
                    item_date = datetime.fromisoformat(item_md).date().isoformat()
                    print("Parsed mailed_date:", item_date)
                except Exception:
                    item_date = (item_md or '')[:-1]

                # if this item's word and date are in the matches, set sent_date
                matched = any((m.get('word','').lower() == item.get('word','').lower() and
                                ((m.get('mailed_date') or m.get('date') or '')[:-1] == (item_md or '')[:-1])) for m in matches)
                if matched:
                    item['sent_date'] = now_iso
                updated.append(item)

            # Save back
            with open(mailed_file, 'w', encoding='utf-8') as f:
                json.dump(updated, f, ensure_ascii=False, indent=2)
            print("Marked mailed entries as sent in mailed.json")
            return {'status': 'emailed_and_marked_sent', 'mailed_words': matches}
            
        except Exception as e:
            print("Warning: could not mark mailed entries as sent:", e)

    except Exception as e:
        print("Failed to send email:", e)
        return {'status': 'failed_to_send_email', 'error': str(e)}