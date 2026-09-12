/**
 * Timeline types (UI-05).
 *
 * TimelineEvent: one node in a biography/heritage/version timeline.
 * Public person events currently project only { event_id, role, description }
 * ([DATA-GAP: assertions/events 字段语义]) — year/place/person/source are
 * optional and appear when content admission provides them.
 */
export interface TimelineEvent {
  /** Stable id (event_id when data-driven). */
  id: string
  /** Node title (event role label or life-phase title). */
  title: string
  /** Optional year / date label. */
  date?: string
  /** Optional place. */
  place?: string
  /** Optional related person. */
  person?: string
  /** Optional source reference. */
  source?: string
  /** Optional detail text. */
  description?: string
}
