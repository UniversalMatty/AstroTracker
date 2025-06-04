"""Utilities for retrieving planet descriptions.

This module stores default descriptions for the Energetic Blueprint system and
provides a mechanism to update them from an external JSON resource.  Set the
``PLANET_DESCRIPTION_URL`` environment variable to a URL containing a JSON
object mapping planet names to description strings.  When the module is
imported, it will attempt to fetch that file and merge the results into the
local descriptions.
"""

from __future__ import annotations

import os
from typing import Dict

import requests

# Base descriptions bundled with the repository -------------------------------
DESCRIPTIONS: Dict[str, str] = {
    "Sun": (
        "The Sun illustrates the seat of personal vitality and purpose. It reveals "
        "how you feel seen and how you compensate when insecurity arises. When "
        "integrated, it guides confidence and warmth; when wounded, it may seek "
        "approval or dominate. This placement highlights the path to authentic "
        "self-expression."
    ),
    "Moon": (
        "The Moon describes your emotional memory and instinctive reactions. It "
        "shows how you soothe yourself when anxious or cling to habits from "
        "childhood. Here we see where you seek safety, sometimes by retreating or "
        "over-nurturing. Awareness fosters emotional regulation and healthier "
        "attachment."
    ),
    "Mercury": (
        "Mercury governs perception and communication patterns. It maps how you "
        "process information and express thoughts under stress. This planet "
        "highlights coping styles like overthinking, humor, or avoidance when "
        "feeling unheard. Understanding Mercury refines your voice and mental "
        "agility."
    ),
    "Venus": (
        "Venus reveals your capacity for love, pleasure, and self-worth. It shows "
        "how you attract connection or build walls to avoid hurt. This placement "
        "influences financial choices and aesthetic preferences. Working with "
        "Venus softens self-judgment and deepens relational harmony."
    ),
    "Mars": (
        "Mars channels your assertive drive and management of anger. It exposes "
        "impulses used to defend, compete, or avoid confrontation. When conscious, "
        "Mars offers courage and healthy boundaries instead of reckless force. "
        "This placement teaches how to pursue desires without harm."
    ),
    "Jupiter": (
        "Jupiter expands your worldview and sense of possibility. It outlines how "
        "optimism or excess shapes your growth. Under stress, you may overreach; "
        "when balanced, you inspire others and explore new horizons. Jupiter "
        "points to experiences that cultivate meaning and generosity."
    ),
    "Saturn": (
        "Saturn symbolizes structure, responsibility, and fear of inadequacy. It "
        "shows where you compensate with hard work or withdrawal due to "
        "self-criticism. By facing these tests patiently, you build resilience and "
        "realistic confidence. Saturn teaches maturity through sustained effort."
    ),
    "Rahu": (
        "Rahu (North Node) depicts yearning for unfamiliar experiences. It can fuel "
        "obsession with novelty or status when insecurity bites. Engaged mindfully, "
        "Rahu promotes bold experimentation and progressive thinking. This point "
        "suggests stepping into discomfort to accelerate growth."
    ),
    "Ketu": (
        "Ketu (South Node) signals ingrained skills and tendencies toward detachment. "
        "You may retreat or undervalue these abilities, seeing them as ordinary. "
        "Recognizing Ketu helps you access quiet expertise without isolation and "
        "invites balance between independence and reliance."
    ),
    "Uranus": (
        "Uranus reflects your urge for freedom and authentic individuality. Sudden "
        "changes or rebellious impulses may surface when you feel restricted. "
        "Expressed consciously, Uranus inspires innovation and unconventional "
        "insight. It teaches adaptability and the courage to break outdated patterns."
    ),
    "Neptune": (
        "Neptune speaks to imagination, spirituality, and sensitivity to collective "
        "moods. It may blur boundaries, leading to escapism or idealization when "
        "reality feels harsh. Channeled well, Neptune fosters compassion, artistic "
        "vision, and subtle perception. This placement encourages discerning "
        "inspiration from illusion."
    ),
    "Pluto": (
        "Pluto reveals core desires for transformation and control. It exposes areas "
        "where power struggles or deep fears push you toward regeneration. "
        "Confronting Pluto's intensity promotes psychological insight and the "
        "ability to release outworn attachments. It guides profound healing through "
        "facing shadow material."
    ),
    "Ascendant": (
        "The Ascendant describes your instinctive approach to life and the impression "
        "you make on others. It reflects coping mechanisms used to protect identity "
        "when under pressure. Embracing its qualities allows authentic presence and "
        "adaptability. This point sets the tone for your personal journey."
    ),
}


def load_external_descriptions(url: str) -> bool:
    """Fetch a JSON mapping of planet descriptions from ``url`` and merge it.

    The fetched JSON must be an object with planet names as keys. New entries
    overwrite any existing defaults.  Returns ``True`` if the fetch succeeds,
    otherwise ``False``.
    """

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            DESCRIPTIONS.update({str(k): str(v) for k, v in data.items()})
            return True
    except Exception as exc:  # pragma: no cover - network issues are non-critical
        print(f"Failed to load external planet descriptions: {exc}")
    return False


# Attempt to load external descriptions if an environment variable is set
_external_url = os.environ.get("PLANET_DESCRIPTION_URL")
if _external_url:
    load_external_descriptions(_external_url)


def get_planet_description(planet_name: str) -> str:
    """Return a practical description for ``planet_name``."""
    return DESCRIPTIONS.get(
        planet_name, f"Description for {planet_name} is not available."
    )


