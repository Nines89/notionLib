from datetime import datetime, timezone, timedelta


def _parse_iso(value: str):
    if not value:
        return None
    text = value.strip().replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def run_prune_old_entries(api, ds_id: str, date_prop: str, days: int) -> list[str]:
    from notion_lib.nModels.datasources import DataSourceFactory
    from notion_lib.nEndpoints.blocks import delete_block

    if days <= 0:
        raise ValueError('I giorni devono essere > 0.')

    ds = DataSourceFactory.find(api.headers, ds_id)
    entries = ds.all_entries()
    if not entries:
        return ['⚠ Nessuna entry trovata nel datasource.']

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    scanned = 0
    deleted = 0
    skipped_no_date = 0

    for entry in entries:
        scanned += 1
        props = entry.get('properties', {})
        date_obj = props.get(date_prop, {}).get('date') if date_prop in props else None
        start = (date_obj or {}).get('start') if isinstance(date_obj, dict) else None
        dt = _parse_iso(start)
        if not dt:
            skipped_no_date += 1
            continue
        if dt < cutoff:
            delete_block(api.headers, entry.get('id'))
            deleted += 1

    return [
        f'✓ Soglia: {days} giorni (prima di {cutoff.date().isoformat()})',
        f'✓ Entry analizzate: {scanned}',
        f'✓ Entry senza data valida: {skipped_no_date}',
        f'✓ Entry eliminate: {deleted}',
    ]
