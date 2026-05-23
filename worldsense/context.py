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

    if any(word in text for word in ["cancella", "delete", "remove", "rm -rf"]):
        signals.append("potentially_destructive_operation")
        constraints.append("rollback_may_be_unavailable")
        missing_information.extend(["exact_target", "backup_available", "user_confirmation"])

    if any(word in text for word in ["miglior", "best", "piu economico", "piu conveniente"]):
        assumptions.append("preference_criteria_are_underspecified")
        missing_information.append("decision_criteria")

    if any(word in text for word in ["costoso", "expensive", "pagamento", "purchase"]):
        signals.append("financial_commitment")
        missing_information.extend(["budget", "purchase_confirmation"])

    if any(word in text for word in ["documento", "numero privato", "private number", "credentials"]):
        signals.append("privacy_sensitive_data")
        constraints.append("data_minimization")
        missing_information.extend(["recipient", "sharing_consent"])

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
