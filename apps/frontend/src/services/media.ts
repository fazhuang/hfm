/**
 * Media display helpers (pre-acceptance demo library).
 */
import { PUBLIC_NAMESPACE } from './api'
import type { MediaCategory } from '../types/media'

/** Bytes endpoint URL for a published media asset (inline display). */
export function mediaBytesUrl(id: string): string {
  return `${PUBLIC_NAMESPACE}/media/${id}/bytes`
}

/** Human-readable size. */
export function formatBytes(bytes: number): string {
  if (bytes >= 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${bytes} B`
}

/** Category display labels. */
export const MEDIA_CATEGORY_LABELS: Record<MediaCategory, string> = {
  paper: '学术论文',
  classic: '古籍版本',
  movie: '影视资料',
  other: '其他',
}

/** True when the asset is a video the browser can play inline. */
export function isPlayableVideo(mime: string): boolean {
  return mime.startsWith('video/')
}
