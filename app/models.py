"""Pydantic models describing what the API returns."""

from pydantic import BaseModel


class WatchlistEntry(BaseModel):
    """One device family we keep an eye on (from data/watchlist.yaml)."""

    name: str
    keywords: list[str]
    product_codes: list[str] = []


class Clearance(BaseModel):
    """A 510(k) premarket notification, trimmed to the useful fields."""

    k_number: str
    device_name: str
    applicant: str
    product_code: str
    decision_date: str
    decision_description: str

    @classmethod
    def from_openfda(cls, record: dict) -> "Clearance":
        """Build a Clearance from one raw openFDA 510(k) result."""
        return cls(
            k_number=record.get("k_number", ""),
            device_name=record.get("device_name", ""),
            applicant=record.get("applicant", ""),
            product_code=record.get("product_code", ""),
            decision_date=record.get("decision_date", ""),
            decision_description=record.get("decision_description", ""),
        )


class Recall(BaseModel):
    """A device recall, trimmed to the useful fields."""

    recall_number: str
    recalling_firm: str
    product_description: str
    reason_for_recall: str
    recall_status: str
    product_code: str
    event_date_initiated: str

    @classmethod
    def from_openfda(cls, record: dict) -> "Recall":
        """Build a Recall from one raw openFDA recall result."""
        return cls(
            recall_number=record.get("product_res_number", ""),
            recalling_firm=record.get("recalling_firm", ""),
            product_description=record.get("product_description", ""),
            reason_for_recall=record.get("reason_for_recall", ""),
            recall_status=record.get("recall_status", ""),
            product_code=record.get("product_code", ""),
            event_date_initiated=record.get("event_date_initiated", ""),
        )
