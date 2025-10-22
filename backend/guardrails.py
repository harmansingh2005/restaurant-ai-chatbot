"""
guardrails.py

Utilities for: loading restaurant YAML, building a system prompt, detecting
canned intents, and post-processing the model output.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Dict, Optional
import re
import yaml


@lru_cache(maxsize=1)
def load_restaurant(path: str = "restaurant.yml") -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def canned_reply(user_text: str, data: Dict) -> Optional[str]:
    """Return a polished canned reply for common intents using strict matching.
    Uses word-boundary regex to avoid false positives (e.g., 'seat' vs 'eat').
    """
    t = (user_text or "").strip().lower()

    # Patterns (word-boundary to prevent substring accidents)
    hours_pat = re.compile(r"\b(hours?|open|closing?|time|today)\b")
    menu_pat = re.compile(r"\b(menu|dishes?|food|foods|specials?)\b")
    address_pat = re.compile(r"\b(address|where|location|directions?|map)\b")
    phone_pat = re.compile(r"\b(phone|call|number|contact)\b")
    dietary_pat = re.compile(r"\b(gluten[- ]?free|nut[- ]?free|allergen|vegan|vegetarian)\b")
    seating_pat = re.compile(r"\b(seat|seating|group|party|booths?|booth|outdoor|patio)\b")
    reserve_pat = re.compile(r"\b(reserve|reservation|book(ing)?|table)\b")

    if hours_pat.search(t):
        hours = data.get("hours", {})
        if hours:
            lines = ["Our hours:"] + [f"- {day.capitalize()}: {val}" for day, val in hours.items()]
            return "\n".join(lines)
        return "We're open daily; please check our website for the latest hours."

    if menu_pat.search(t):
        url = data.get("menu_url")
        if url:
            return f"You can view our menu here: {url}"
        return "We offer family-style classics and daily specials. Ask us about today's picks!"

    if address_pat.search(t):
        addr = data.get("address")
        return f"We're located at: {addr}. Parking is available nearby." if addr else None

    if phone_pat.search(t):
        phone = data.get("phone")
        return f"You can reach us at {phone}." if phone else None

    if dietary_pat.search(t):
        diet = data.get("dietary", {})
        parts = []
        if diet.get("gluten_free", True):
            parts.append("gluten-free")
        if diet.get("nut_free", True):
            parts.append("nut-free")
        if diet.get("vegetarian", True):
            parts.append("vegetarian")
        vegan = diet.get("vegan")
        if vegan:
            parts.append("vegan options") if vegan is True else parts.append("vegan upon request")
        joined = ", ".join(parts) if parts else "several dietary"
        return f"Yes, we offer {joined} options. Please let your server know about any allergies so we can guide you."

    if seating_pat.search(t) or reserve_pat.search(t):
        seating = data.get("seating", {})
        outdoor = seating.get("outdoor")
        booths = seating.get("booths")
        reservations = data.get("reservations")

        bits = []
        if reservations is True:
            bits.append("We accept reservations.")
        elif reservations is False:
            bits.append("We don’t take reservations; walk-ins are welcome.")
        elif isinstance(reservations, str) and reservations:
            bits.append(reservations)

        if outdoor is True:
            bits.append("We have outdoor seating.")
        if booths is True:
            bits.append("Booths are available.")

        phone = data.get("phone")
        if not bits:
            bits.append("Seating availability varies by time and party size.")
        follow = f" For large groups, please call {phone}." if phone else " For large groups, please call ahead."
        return " ".join(bits) + follow

    return None


def build_system_prompt(data: Dict) -> str:
    name = data.get("name", "the restaurant")
    address = data.get("address", "")
    phone = data.get("phone", "")
    notes = data.get("notes", "")
    dietary = data.get("dietary", {})
    seating = data.get("seating", {})
    reservations = data.get("reservations", "")
    return (
        "You are a helpful, concise assistant for a restaurant website."
        " Use the restaurant profile truthfully and keep answers short (1–2 sentences)."
        f" Restaurant: {name}. Address: {address}. Phone: {phone}. "
        f"Dietary: {dietary}. Seating: {seating}. Reservations: {reservations}. "
        f"Notes: {notes}"
    )


def postprocess(text: str) -> str:
    """Simple cleanup hook."""
    return (text or "").strip()
