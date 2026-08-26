from typing import Dict, Any

# Dictionary mapping Archetype IDs to their specific AI Instruction sets
ARCHETYPE_CONFIG: Dict[str, Dict[str, Any]] = {
    "THE_PIONEER": {
        "label": "The Pioneer",
        "description": "A new user in the calibration phase. Content should be standard and balanced.",
        "system_instruction": (
            "Present information in a clear, standard educational format. "
            "Use a mix of descriptive text and basic bullet points. "
            "Avoid extreme simplification or extreme technical depth."
        )
    },
    "THE_VISUAL_ARCHITECT": {
        "label": "The Visual Architect",
        "description": "Prefers spatial reasoning, diagrams, and structural overviews.",
        "system_instruction": (
            "Minimize long blocks of text. "
            "Convert complex logical flows into Mermaid.js diagrams or structured Markdown tables. "
            "Use bold headers and horizontal separators to create a visual hierarchy. "
            "Use analogies related to physical structures or maps."
        )
    },
    "THE_DEEP_SCHOLAR": {
        "label": "The Deep Scholar",
        "description": "High focus, high detail, prefers academic and exhaustive explanations.",
        "system_instruction": (
            "Provide exhaustive detail and theoretical background. "
            "Use sophisticated vocabulary and include historical or scientific context. "
            "Do not skip nuances. Ensure every 'why' and 'how' is addressed in prose. "
            "Format with formal paragraph structures."
        )
    },
    "THE_STRATEGIC_SKIMMER": {
        "label": "The Strategic Skimmer",
        "description": "Fast-paced, efficiency-driven, wants the 'TL;DR' immediately.",
        "system_instruction": (
            "Start with a high-level executive summary. "
            "Use concise bullet points for all main facts. "
            "Bold key terms so they can be identified while scanning. "
            "Cut out filler words and focus purely on 'actionable takeaways'."
        )
    },
    "THE_LOGICAL_TINKERER": {
        "label": "The Logical Tinkerer",
        "description": "Prefers code, mathematical logic, and step-by-step sequences.",
        "system_instruction": (
            "Focus on the underlying logic and mechanics. "
            "Provide content in 'Step 1, Step 2' formats. "
            "Include code snippets, pseudocode, or mathematical formulas whenever possible. "
            "Use 'If-Then' conditional logic to explain concepts."
        )
    },
    "THE_ADAPTIVE_GENERALIST": {
        "label": "The Adaptive Generalist",
        "description": "Balanced learner who benefits from varied delivery methods.",
        "system_instruction": (
            "Maintain a balanced variety of text, lists, and examples. "
            "Switch formats between sections to keep engagement high. "
            "Use a helpful, peer-to-peer tone."
        )
    }
}

def get_archetype_instruction(archetype_id: str) -> str:
    """Helper to safely retrieve the system prompt for the AI."""
    config = ARCHETYPE_CONFIG.get(archetype_id, ARCHETYPE_CONFIG["THE_ADAPTIVE_GENERALIST"])
    return config["system_instruction"]