# notion_lib/nModels/blocks/meeting_notes.py
from enum import Enum

from notion_lib.nModels.blocks.base_block import register_block, BlockImpl
from notion_lib.nTypes import NRichList
from notion_lib.nTypes.rich_text import create_rich_list
from notion_lib.nTypes.primitives import NDate


class MeetingNotesStatus(Enum):
    NOT_STARTED = "transcription_not_started"
    PAUSED = "transcription_paused"
    IN_PROGRESS = "transcription_in_progress"
    SUMMARY_IN_PROGRESS = "summary_in_progress"
    NOTES_READY = "notes_ready"


@register_block("meeting_notes")
@register_block("transcription")
class MeetingNotesBlock(BlockImpl):
    type = "meeting_notes"
    supports_children = True
    updatable = False

    def __init__(self,
                 headers,
                 block_id=None,
                 title: NRichList = None,
                 status: str = None,
                 summary_block_id: str = None,
                 notes_block_id: str = None,
                 transcript_block_id: str = None,
                 calendar_start: str = None,
                 calendar_end: str = None,
                 attendees: list = None,
                 recording_start: str = None,
                 recording_end: str = None):
        super().__init__(headers, block_id)
        self._title = title or NRichList()
        self._status = status
        self._summary_block_id = summary_block_id
        self._notes_block_id = notes_block_id
        self._transcript_block_id = transcript_block_id
        self._calendar_start = calendar_start
        self._calendar_end = calendar_end
        self._attendees = attendees or []
        self._recording_start = recording_start
        self._recording_end = recording_end

    @classmethod
    def from_data(cls, headers, data, block_id):
        # compatibilità con vecchia versione API (transcription -> meeting_notes)
        block_type = data["type"]
        p = data[block_type]

        children = p.get("children", {})
        calendar = p.get("calendar_event", {})
        recording = p.get("recording", {})

        obj = cls(
            headers=headers,
            block_id=block_id,
            title=create_rich_list(p.get("title", [])),
            status=p.get("status"),
            summary_block_id=children.get("summary_block_id"),
            notes_block_id=children.get("notes_block_id"),
            transcript_block_id=children.get("transcript_block_id"),
            calendar_start=calendar.get("start_time"),
            calendar_end=calendar.get("end_time"),
            attendees=calendar.get("attendees", []),
            recording_start=recording.get("start_time"),
            recording_end=recording.get("end_time"),
        )
        obj._data = data
        return obj

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("MeetingNotesBlock is read-only and cannot be created via API.")

    def to_payload(self):
        raise NotImplementedError("MeetingNotesBlock is read-only and cannot be updated via API.")

    def update(self):
        raise NotImplementedError("MeetingNotesBlock is read-only and cannot be updated via API.")

    # --- properties ---

    @property
    def title(self) -> str:
        return self._title.text

    @property
    def status(self) -> MeetingNotesStatus:
        return MeetingNotesStatus(self._status) if self._status else None

    @property
    def is_ready(self) -> bool:
        return self._status == MeetingNotesStatus.NOTES_READY.value

    @property
    def attendees(self) -> list:
        return self._attendees

    @property
    def calendar_start(self) -> NDate:
        return NDate(self._calendar_start) if self._calendar_start else None

    @property
    def calendar_end(self) -> NDate:
        return NDate(self._calendar_end) if self._calendar_end else None

    @property
    def recording_start(self) -> NDate:
        return NDate(self._recording_start) if self._recording_start else None

    @property
    def recording_end(self) -> NDate:
        return NDate(self._recording_end) if self._recording_end else None

    # --- accesso ai contenuti tramite child block IDs ---

    def get_summary(self):
        """Recupera il blocco summary. None se non disponibile."""
        if not self._summary_block_id:
            return None
        from notion_lib.nModels.blocks.base_block import NFactory
        return NFactory.find(self.headers, self._summary_block_id)

    def get_notes(self):
        """Recupera il blocco notes. None se non disponibile."""
        if not self._notes_block_id:
            return None
        from notion_lib.nModels.blocks.base_block import NFactory
        return NFactory.find(self.headers, self._notes_block_id)

    def get_transcript(self):
        """Recupera il blocco transcript. None se non disponibile."""
        if not self._transcript_block_id:
            return None
        from notion_lib.nModels.blocks.base_block import NFactory
        return NFactory.find(self.headers, self._transcript_block_id)

    def __repr__(self):
        return (
            f"<MeetingNotesBlock"
            f" title='{self.title}'"
            f" status={self.status}"
            f" is_ready={self.is_ready}>"
        )

