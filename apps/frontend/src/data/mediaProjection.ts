/**
 * Production media projection — governed per-media source record → public
 * media item (UX2-P1 F-5 closure).
 *
 * Canonical frontend equivalent of the backend public media projection
 * (`apps/backend/src/hfm/api/v1/phase1.py` `public_media`): reads the governed
 * per-media source records (`archiveInventory.ts` `ARCHIVE_MEDIA_RECORDS`) and
 * applies the same production rules as the backend endpoint:
 *
 *   - category derived from the object-key path (论文 → paper, 电影 → movie,
 *     论著/版本 → classic, else other) — the backend's exact rule;
 *   - name from the governed title;
 *   - pass-through of mime_type / byte_size / rights / license / object_key /
 *     id from the governed record;
 *   - only published-projection records are returned (public_projection
 *     semantics; the governed movie records are AVAILABLE → published).
 *
 * This transformation lives in production data paths and is consumed by tests
 * through the same runtime path as production (`fetchPublicMedia` transport).
 */
import type { MediaAssetItem, MediaCategory } from '../types/media'
import { ARCHIVE_MEDIA_RECORDS } from './archiveInventory'

/** Backend category rule — derived from the object-key path (phase1.py). */
export function categoryFromObjectKey(objectKey: string): MediaCategory {
  if (objectKey.includes('论文')) return 'paper'
  if (objectKey.includes('电影')) return 'movie'
  if (objectKey.includes('论著') || objectKey.includes('版本')) return 'classic'
  return 'other'
}

/** Public media projection over the governed per-media source records. */
export function projectPublicMedia(kind?: MediaCategory): MediaAssetItem[] {
  return ARCHIVE_MEDIA_RECORDS.filter(
    (record) => kind === undefined || categoryFromObjectKey(record.objectKey) === kind,
  ).map((record) => ({
    id: record.id,
    name: record.title,
    object_key: record.objectKey,
    mime_type: record.mimeType,
    byte_size: record.byteSize,
    rights_holder: record.rightsHolder,
    license_basis: record.licenseBasis,
    restriction: null,
    category: categoryFromObjectKey(record.objectKey),
    publication_state: 'published',
  }))
}
