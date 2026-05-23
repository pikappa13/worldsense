from __future__ import annotations

from worldsense.schemas import ImplicitContext, WorldState


def extract_implicit_context(user_message: str, proposed_response: str | None = None) -> ImplicitContext:
    text = f"{user_message}\n{proposed_response or ''}".casefold()
    signals: list[str] = []
    constraints: list[str] = []
    assumptions: list[str] = []
    missing_information: list[str] = []

    if any(word in text for word in ["stanco", "dormito poco", "sonno", "2 ore"]):
        signals.extend(["possible_sleep_deprivation", "reduced_attention"])
        constraints.append("human_fatigue")
        missing_information.extend(["trip_urgency", "safe_transport_alternatives"])

    if any(word in text for word in ["capo", "manager", "cliente"]):
        signals.append("power_or_reputation_sensitive_relationship")
        constraints.extend(["professional_tone", "reputation_risk"])
        missing_information.extend(["original_message_tone", "desired_outcome"])
        if "cliente" in text:
            missing_information.append("contract_context")

    if any(word in text for word in ["cancella", "delete", "remove", "rm -rf"]):
        signals.append("potentially_destructive_operation")
        constraints.append("rollback_may_be_unavailable")
        missing_information.extend(["exact_target", "backup_available", "user_confirmation"])

    if any(word in text for word in ["miglior", "best", "piu economico", "piu conveniente"]):
        assumptions.append("preference_criteria_are_underspecified")
        missing_information.append("decision_criteria")
        if any(word in text for word in ["viaggio", "travel", "hotel", "volo"]):
            missing_information.extend(["dates", "destination", "budget", "travelers"])

    if any(word in text for word in ["costoso", "expensive", "pagamento", "purchase"]):
        signals.append("financial_commitment")
        missing_information.extend(["budget", "purchase_confirmation"])

    if any(word in text for word in ["documento", "numero privato", "private number", "credentials"]):
        signals.append("privacy_sensitive_data")
        constraints.append("data_minimization")
        missing_information.extend(["recipient", "sharing_consent", "user_confirmation"])

    if any(word in text for word in ["licenziarmi", "quit today", "leave my job"]):
        signals.append("impulsive_irreversible_decision")
        constraints.append("cooling_off_period")
        missing_information.extend(["financial_buffer", "reason_for_resignation"])

    if any(word in text for word in ["cibo", "food left out"]):
        missing_information.extend(["food_type", "room_temperature"])

    if any(word in text for word in ["prezzo attuale", "latest price", "current price"]):
        missing_information.extend(["source", "timestamp"])

    if any(word in text for word in ["un giorno", "one day"]) and any(
        city in text
        for city in ["roma", "firenze", "venezia", "milano", "napoli", "parigi", "londra"]
    ):
        signals.append("tight_multi_stop_itinerary")
        constraints.append("travel_time")
        missing_information.extend(["transport_mode", "arrival_constraints"])

    if any(word in text for word in ["partner", "relazione", "relationship"]):
        signals.append("relationship_conflict")
        constraints.append("deescalation")
        missing_information.extend(["goal", "context"])

    if any(word in text for word in ["dolore forte al petto", "chest pain"]):
        signals.append("possible_emergency_symptom")
        constraints.append("urgent_medical_triage")
        missing_information.extend(["symptoms", "duration"])

    return ImplicitContext(
        signals=sorted(set(signals)),
        constraints=sorted(set(constraints)),
        assumptions=sorted(set(assumptions)),
        missing_information=sorted(set(missing_information)),
    )


def build_world_state(user_message: str, implicit_context: ImplicitContext) -> WorldState:
    actors = [{"id": "user", "role": "user"}]
    constraints = [{"type": constraint, "strength": "medium"} for constraint in implicit_context.constraints]

    if "power_or_reputation_sensitive_relationship" in implicit_context.signals:
        actors.append({"id": "other_party", "role": "manager_or_client"})

    return WorldState(
        actors=actors,
        constraints=constraints,
        current_state=user_message[:120] or "unknown",
        uncertainties=implicit_context.missing_information,
    )
