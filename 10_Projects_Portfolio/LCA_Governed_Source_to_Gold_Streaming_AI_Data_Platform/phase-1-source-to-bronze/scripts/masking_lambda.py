"""
Masking Lambda — Phase 1, Entry 2
Applies ADR-001 (mask/tokenize on write) to a raw chat interaction
BEFORE it is written to the DynamoDB staging table.

This function sits between "application generates the interaction"
and "record is written to DynamoDB" in the flow:

    User question -> App generates answer -> [THIS LAMBDA] -> DynamoDB

Two different treatments, deliberately not the same operation:
  - user_id            -> TOKENIZED (reversible, needed to group a user's history)
  - free-text fields    -> MASKED (irreversible, no legitimate need to recover it)
"""

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone

import boto3

kms_client = boto3.client("kms")
KMS_KEY_ID = "alias/interaction-tokenization-key"  # replace with real key alias

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_PATTERN = re.compile(r"\b\d{10}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")


def tokenize_user_id(raw_user_id: str) -> str:
    """
    Reversible tokenization via KMS envelope encryption.
    Used for user_id specifically, because downstream needs to group
    interactions by the same user without ever seeing who that user is.
    """
    encrypted = kms_client.encrypt(KeyId=KMS_KEY_ID, Plaintext=raw_user_id.encode())
    return "tok_" + encrypted["CiphertextBlob"].hex()[:32]


def mask_pii_in_text(text: str) -> str:
    """
    Irreversible masking of PII patterns found inside free text.
    Applied to user_question / generated_answer, since a user may
    voluntarily type an email, phone number, or similar into a chat.
    There is no legitimate downstream need to recover the original value.
    """
    text = EMAIL_PATTERN.sub("[EMAIL_REDACTED]", text)
    text = PHONE_PATTERN.sub("[PHONE_REDACTED]", text)
    return text


def compute_payload_hash(payload: dict) -> str:
    """SHA-256 of the payload, for the same dedup pattern used elsewhere in this project."""
    canonical = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


def build_governed_record(raw_event: dict) -> dict:
    """
    Takes a raw interaction as produced by the application, and returns
    the fully governed, envelope-wrapped record ready for DynamoDB.
    """
    now = datetime.now(timezone.utc).isoformat()

    masked_payload = {
        "user_question": mask_pii_in_text(raw_event["user_question"]),
        "generated_answer": mask_pii_in_text(raw_event["generated_answer"]),
        "answer_timestamp": raw_event["answer_timestamp"],
        "channel": raw_event.get("channel", "unknown"),
        "model": raw_event.get("model", "unknown"),
    }

    governed_record = {
        "event_id": raw_event.get("interaction_id", str(uuid.uuid4())),
        "event_type": "chat_interaction",
        "event_source": raw_event.get("producer_id", "chatbot_app"),
        "event_timestamp": raw_event["question_timestamp"],
        "ingest_timestamp": now,
        "schema_version": "v1",
        "producer_id": raw_event.get("producer_id", "chatbot_app"),
        "user_id": tokenize_user_id(raw_event["user_id"]),
        "session_id": raw_event["session_id"],
        "device_id": None,
        "geo_country": raw_event.get("geo_country"),
        "payload": masked_payload,
        "payload_hash": compute_payload_hash(masked_payload),
        "is_pii": True,
        "processing_status": "PENDING",
        "retry_count": 0,
    }
    return governed_record


def lambda_handler(event, context):
    """
    Entry point. Expects the raw interaction as the event body,
    returns the governed record ready to be written to DynamoDB
    by the calling application (or writes it directly — see note below).
    """
    governed_record = build_governed_record(event)

    # NOTE: this function currently returns the governed record rather than
    # writing it directly, so the application controls the DynamoDB write
    # (e.g. as part of a larger transaction). If a direct write is preferred,
    # add a boto3 DynamoDB put_item call here using the table design in
    # dynamodb-table-design.md.

    return {
        "statusCode": 200,
        "body": governed_record,
    }
