# notion_lib/nModels/blocks/meeting_notes.py
from enum import Enum

from nModels.blocks.base_block import register_block, BlockImpl
from nTypes import NRichList
from nTypes.rich_text import create_rich_list
from nTypes.primitives import NDate


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
        from nModels.blocks.base_block import NFactory
        return NFactory.find(self.headers, self._summary_block_id)

    def get_notes(self):
        """Recupera il blocco notes. None se non disponibile."""
        if not self._notes_block_id:
            return None
        from nModels.blocks.base_block import NFactory
        return NFactory.find(self.headers, self._notes_block_id)

    def get_transcript(self):
        """Recupera il blocco transcript. None se non disponibile."""
        if not self._transcript_block_id:
            return None
        from nModels.blocks.base_block import NFactory
        return NFactory.find(self.headers, self._transcript_block_id)

    def __repr__(self):
        return (
            f"<MeetingNotesBlock"
            f" title='{self.title}'"
            f" status={self.status}"
            f" is_ready={self.is_ready}>"
        )


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

    from client.auth import NotionApiClient
    from nModels.blocks.base_block import NFactory
    from nEndpoints.pages import get_block_children
    from nEndpoints.searches import search_by_title

    api = NotionApiClient(key="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")

    # -----------------------------------------------------------------------
    # STEP 1 — Cercare una pagina che contiene meeting notes
    # -----------------------------------------------------------------------
    # Il modo più semplice per trovare un blocco meeting_notes è cercare
    # una pagina che sai contenere note di riunione generate da Notion AI,
    # poi iterare sui suoi figli finché non trovi il blocco giusto.
    #
    # Sostituisci "NOME_PAGINA" con il titolo della tua pagina con meeting notes.
    #
    # results = search_by_title(api.headers, "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7#325b7a8f7294804d9bfdf561ee90b11f", filters="page")
    # for r in results['results']:
    #     print(r['id'], r['properties']['title'])

    # -----------------------------------------------------------------------
    # STEP 2 — Trovare il blocco meeting_notes dentro la pagina
    # -----------------------------------------------------------------------
    # Una volta che hai l'ID della pagina, scorri i suoi figli e cerca
    # il blocco di tipo meeting_notes (o transcription se usi API < 2026-03-11)
    #
    # page_id = "IL_TUO_PAGE_ID"
    # children = get_block_children(api.headers, page_id)
    # for blk in children:
    #     print(blk['type'], blk['id'])
    #     if blk['type'] in ('meeting_notes', 'transcription'):
    #         print("Trovato!", blk['id'])

    # -----------------------------------------------------------------------
    # STEP 3 — Una volta che hai l'ID del blocco, testa così:
    # -----------------------------------------------------------------------
    obj_meeting = "https://www.notion.so/color-A2DCEE-textbf-API-Integration-2a7b7a8f729480b3b420f8736c4116d7?source=copy_link#325b7a8f72948037bc72dfd0a8726941"
    meeting = NFactory.find(api.headers, obj_meeting)

    print(meeting)                    # __repr__
    print("Titolo:   ", meeting.title)
    print("Status:   ", meeting.status)
    print("Pronto:   ", meeting.is_ready)
    print("Inizio:   ", meeting.calendar_start)
    print("Fine:     ", meeting.calendar_end)
    print("Partecip.:", meeting.attendees)
    print("Rec start:", meeting.recording_start)
    print("Rec end:  ", meeting.recording_end)

    # Recupera i contenuti solo se il meeting è pronto
    if meeting.is_ready:
        summary = meeting.get_summary()
        notes = meeting.get_notes()
        transcript = meeting.get_transcript()

        if summary:
            print("Summary children:", summary.get_children())
        if notes:
            print("Notes children:", notes.get_children())
        if transcript:
            print("Transcript children:", transcript.get_children())
    # OUTPUT
    """
    <MeetingNotesBlock title='Transcription Feature Testing 2026-03-16' status=MeetingNotesStatus.NOTES_READY is_ready=True>
    Titolo:    Transcription Feature Testing 2026-03-16
    Status:    MeetingNotesStatus.NOTES_READY
    Pronto:    True
    Inizio:    None
    Fine:      None
    Partecip.: []
    Rec start: 2026-03-16 11:57:00+00:00
    Rec end:   2026-03-16 11:58:00+00:00
    Summary children: [<nModels.blocks.paragraph.ParagraphBlock object at 0x000001C43619ED70>, <nModels.blocks.paragraph.ParagraphBlock object at 0x000001C43619EFD0>, <nModels.blocks.paragraph.ParagraphBlock object at 0x000001C4361C0B90>, <nModels.blocks.base_block.UnsupportedBlock object at 0x000001C4361AC590>, <nModels.blocks.base_block.UnsupportedBlock object at 0x000001C4361B3890>, <nModels.blocks.base_block.UnsupportedBlock object at 0x000001C4361B3C50>, <nModels.blocks.base_block.UnsupportedBlock object at 0x000001C43619F6F0>, <nModels.blocks.base_block.UnsupportedBlock object at 0x000001C43619F950>, <nModels.blocks.base_block.UnsupportedBlock object at 0x000001C4361C0710>]
    Notes children: [<nModels.blocks.paragraph.ParagraphBlock object at 0x000001C4361379B0>]
    Transcript children: [<nModels.blocks.paragraph.ParagraphBlock object at 0x000001C4361379B0>]
    """
    pass