
from app.core.config import get_settings
from app.data.session_store import get_or_create_session, set_session
from app.services.ai_service import get_ai_service


class ConversationBufferMemory:

    def add_turn(
        self,
        user_id: str,
        session_id: str,
        human_role: str,
        human_message: str,
        ai_role: str,
        ai_message: str,
    ) -> None:
        session = get_or_create_session(user_id, session_id)
        session["messages"].append(
            {"role": human_role, "message": human_message}
        )
        session["messages"].append({"role": ai_role, "message": ai_message})

    def get_context(self, user_id: str, session_id: str) -> str:
        session = get_or_create_session(user_id, session_id)
        messages = session["messages"]
        summary = session.get("summary")
        if summary:
            lines = [f"[Earlier summary] {summary}"]
            for m in messages:
                lines.append(f"{m.get('role', '')}: {m.get('message', '')}")
            return "\n".join(lines)
        if not messages:
            return ""
        return "\n".join(
            f"{m.get('role', '')}: {m.get('message', '')}" for m in messages
        )

    def get_turns_for_summary(self, user_id: str, session_id: str) -> list[dict]:
        session = get_or_create_session(user_id, session_id)
        return session["messages"].copy()

    def summarize_if_needed(self, user_id: str, session_id: str) -> None:
        settings = get_settings()
        session = get_or_create_session(user_id, session_id)
        messages = session["messages"]
        if len(messages) < settings.memory_max_turns:
            return
        keep = settings.memory_keep_last * 2
        to_summarize = messages[:-keep]
        if not to_summarize:
            return
        summary = get_ai_service().summarize_conversation(to_summarize)
        session["summary"] = summary
        session["messages"] = messages[-keep:]
        set_session(user_id, session_id, session)
