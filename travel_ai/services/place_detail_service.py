import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from gtts import gTTS
from gtts.lang import tts_langs

from travel_ai.prompts.system_prompts import SYSTEM_PROMPT_PLACE_DETAIL
from travel_ai.services.llm_service import generate_content


CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" / "place.detail.output"

CITY_LOCAL_LANG = {
    "pune": ("Marathi", "mr"),
    "mumbai": ("Marathi", "mr"),
    "nagpur": ("Marathi", "mr"),
    "nashik": ("Marathi", "mr"),
    "kolhapur": ("Marathi", "mr"),
    "satara": ("Marathi", "mr"),
    "delhi": ("Hindi", "hi"),
    "agra": ("Hindi", "hi"),
    "jaipur": ("Hindi", "hi"),
    "lucknow": ("Hindi", "hi"),
    "varanasi": ("Hindi", "hi"),
    "hyderabad": ("Telugu", "te"),
    "vijayawada": ("Telugu", "te"),
    "chennai": ("Tamil", "ta"),
    "madurai": ("Tamil", "ta"),
    "coimbatore": ("Tamil", "ta"),
    "bangalore": ("Kannada", "kn"),
    "mysore": ("Kannada", "kn"),
    "kochi": ("Malayalam", "ml"),
    "thiruvananthapuram": ("Malayalam", "ml"),
    "kolkata": ("Bengali", "bn"),
    "guwahati": ("Assamese", "as"),
    "ahmedabad": ("Gujarati", "gu"),
    "vadodara": ("Gujarati", "gu"),
    "amritsar": ("Punjabi", "pa"),
}


def _canonical_key(city: str, place: str) -> str:
    raw = f"{city}_{place}".strip().lower()
    raw = re.sub(r"[^a-z0-9]+", "_", raw)
    return raw.strip("_")


def _clean_json(raw: str) -> Dict[str, Any]:
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output")
    return json.loads(match.group(0))


def _generate_tts_file(text: str, file_path: Path, language: str, tld: str = "co.in") -> None:
    tts = gTTS(text=text, lang=language, tld=tld)
    tts.save(str(file_path))


def _contains_native_script(text: str, lang_code: str) -> bool:
    ranges = {
        "hi": (0x0900, 0x097F),  # Devanagari
        "mr": (0x0900, 0x097F),  # Devanagari
        "bn": (0x0980, 0x09FF),  # Bengali
        "ta": (0x0B80, 0x0BFF),  # Tamil
        "te": (0x0C00, 0x0C7F),  # Telugu
        "kn": (0x0C80, 0x0CFF),  # Kannada
        "ml": (0x0D00, 0x0D7F),  # Malayalam
        "gu": (0x0A80, 0x0AFF),  # Gujarati
        "pa": (0x0A00, 0x0A7F),  # Gurmukhi
        "as": (0x0980, 0x09FF),  # Assamese (Bengali-Assamese block)
    }
    if lang_code not in ranges:
        return True
    start, end = ranges[lang_code]
    return any(start <= ord(ch) <= end for ch in text)


async def _regenerate_local_in_native_script(
    english_text: str,
    local_language_name: str,
    lang_code: str,
) -> str:
    prompt = (
        "Translate the following narration into "
        f"{local_language_name} using ONLY native script (no English letters, no transliteration). "
        "Keep facts unchanged and keep output between 120-190 words. "
        "Return STRICT JSON only: {\"local_text\": \"string\"}"
    )
    raw = await generate_content(prompt, english_text)
    parsed = _clean_json(raw)
    return str(parsed.get("local_text", "")).strip()


def _resolve_local_language(city: str) -> Dict[str, str]:
    canonical = _canonical_key(city, "").rstrip("_")
    lang_name, lang_code = CITY_LOCAL_LANG.get(canonical, ("Local", "en"))
    supported = tts_langs()
    if lang_code not in supported:
        return {"name": "Local", "code": "en"}
    return {"name": lang_name, "code": lang_code}


def _build_audio_artifacts(cache_key: str) -> Dict[str, Dict[str, str]]:
    return {
        "english": {
            "audio_file": str(CACHE_DIR / f"{cache_key}_en.mp3"),
            "audio_url": f"/cache/place.detail.output/{cache_key}_en.mp3",
            "lang_code": "en",
        },
        "hindi": {
            "audio_file": str(CACHE_DIR / f"{cache_key}_hi.mp3"),
            "audio_url": f"/cache/place.detail.output/{cache_key}_hi.mp3",
            "lang_code": "hi",
        },
    }


def _to_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _default_constraints(place: str) -> list[str]:
    text = place.lower()
    if any(word in text for word in ["temple", "mandir", "devi", "ganapati", "dargah", "masjid", "church"]):
        return [
            "Follow site-specific darshan/prayer timings before planning arrival.",
            "Some sanctum areas may restrict photography and videography.",
        ]
    if any(word in text for word in ["fort", "hill", "peak", "viewpoint"]):
        return [
            "Check weather and entry timing before departure.",
            "Some sections may have uneven steps or restricted zones.",
        ]
    return [
        "Verify latest opening hours and ticket policy before visiting.",
    ]


def _default_special_cautions(place: str) -> list[str]:
    text = place.lower()
    if any(word in text for word in ["temple", "mandir", "devi", "ganapati", "dargah", "masjid", "church"]):
        return [
            "Wear modest, tradition-appropriate clothing at religious premises.",
            "Remove footwear where required and maintain silence near sanctum/prayer spaces.",
        ]
    if any(word in text for word in ["fort", "hill", "peak", "viewpoint"]):
        return [
            "Use sturdy footwear and carry water for stairs/uneven terrain.",
            "Avoid risky edges and low-light climbs, especially in monsoon.",
        ]
    return [
        "Respect local rules and security guidance on-site.",
    ]


def _apply_royal_honorifics(text: str) -> str:
    replacements = [
        (r"\bchhatrapati\s+shivaji\b(?!\s+maharaj)", "Chhatrapati Shivaji Maharaj"),
        (r"\bshivaji\b(?!\s+maharaj)", "Shivaji Maharaj"),
        (r"\bsambhaji\b(?!\s+maharaj)", "Sambhaji Maharaj"),
        (r"\bmaharana\s+pratap\b(?!\s+maharaj)", "Maharana Pratap Maharaj"),
        (r"\bpratap\b(?!\s+maharaj)", "Pratap Maharaj"),
    ]
    out = text
    for pattern, replacement in replacements:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    return out


async def get_place_detail_with_tts(payload: Dict[str, Any]) -> Dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    place = str(payload.get("place", "")).strip()
    city = str(payload.get("destination_city", "")).strip()
    time_slot = str(payload.get("time", "")).strip()
    reason = str(payload.get("reason_for_time_choice", "")).strip()
    image_url = str(payload.get("image_url", "")).strip()
    cache_key = _canonical_key(city, place)
    json_path = CACHE_DIR / f"{cache_key}.json"
    local_lang = _resolve_local_language(city)
    audio = _build_audio_artifacts(cache_key)

    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        cached_outputs = cached.get("outputs", {})
        local_cached_text = str(cached.get("local_text", "")).strip()
        english_ok = cached_outputs.get("english", {}).get("audio_file") and Path(cached_outputs["english"]["audio_file"]).exists()
        hindi_ok = cached_outputs.get("hindi", {}).get("audio_file") and Path(cached_outputs["hindi"]["audio_file"]).exists()
        local_script_ok = _contains_native_script(local_cached_text, local_lang["code"])
        if english_ok and hindi_ok and local_script_ok:
            return {
                "place": place,
                "destination_city": city,
                "local_language": cached.get("local_language", local_lang["name"]),
                "local_text": local_cached_text,
                "constraints": _to_str_list(cached.get("constraints")) or _default_constraints(place),
                "special_cautions": _to_str_list(cached.get("special_cautions")) or _default_special_cautions(place),
                "outputs": cached_outputs,
                "cached": True,
            }

    llm_input = {
        "place": place,
        "destination_city": city,
        "time_slot": time_slot,
        "reason_for_time_choice": reason,
        "image_url": image_url,
        "local_language_hint": local_lang["name"],
    }
    raw = await generate_content(SYSTEM_PROMPT_PLACE_DETAIL, json.dumps(llm_input))
    parsed = _clean_json(raw)
    english_text = str(parsed.get("english_text", "")).strip()
    hindi_text = str(parsed.get("hindi_text", "")).strip()
    local_text = str(parsed.get("local_text", "")).strip()
    local_language_name = str(parsed.get("local_language_name", "")).strip() or local_lang["name"]
    constraints = _to_str_list(parsed.get("constraints")) or _default_constraints(place)
    special_cautions = _to_str_list(parsed.get("special_cautions")) or _default_special_cautions(place)

    if not english_text or not hindi_text or not local_text:
        raise ValueError("Failed to generate place detail narration text")

    fort_context = "fort" in place.lower() or "fort" in reason.lower()
    if fort_context:
        english_text = _apply_royal_honorifics(english_text)
        hindi_text = _apply_royal_honorifics(hindi_text)
        local_text = _apply_royal_honorifics(local_text)

    if not _contains_native_script(local_text, local_lang["code"]):
        repaired_local = await _regenerate_local_in_native_script(
            english_text=english_text,
            local_language_name=local_language_name,
            lang_code=local_lang["code"],
        )
        if repaired_local:
            local_text = repaired_local

    await asyncio.gather(
        asyncio.to_thread(
            _generate_tts_file,
            english_text,
            Path(audio["english"]["audio_file"]),
            audio["english"]["lang_code"],
            "com",
        ),
        asyncio.to_thread(
            _generate_tts_file,
            hindi_text,
            Path(audio["hindi"]["audio_file"]),
            audio["hindi"]["lang_code"],
            "co.in",
        ),
    )

    outputs = {
        "english": {
            "text": english_text,
            "audio_file": audio["english"]["audio_file"],
            "audio_url": audio["english"]["audio_url"],
        },
        "hindi": {
            "text": hindi_text,
            "audio_file": audio["hindi"]["audio_file"],
            "audio_url": audio["hindi"]["audio_url"],
        },
    }

    cache_doc = {
        "place": place,
        "destination_city": city,
        "local_language": local_language_name,
        "local_text": local_text,
        "constraints": constraints,
        "special_cautions": special_cautions,
        "outputs": outputs,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cache_doc, f, ensure_ascii=False, indent=2)

    return {
        "place": place,
        "destination_city": city,
        "local_language": local_language_name,
        "local_text": local_text,
        "constraints": constraints,
        "special_cautions": special_cautions,
        "outputs": outputs,
        "cached": False,
    }
