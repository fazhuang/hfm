/**
 * Shared API type contracts (migrated Batch 2 asset — ADAPT).
 *
 * Source: HFB `packages/types/src/index.ts` @ `03755b5` (generic subset).
 * Adapted: removed HFB domain types (Document, Person) and the @hfb namespace;
 * kept the generic API/pagination/utility contracts only.
 */

/** Standard API response envelope */
export interface ApiResponse<T> {
  data: T
  meta: ApiMeta
}

/** Pagination metadata */
export interface ApiMeta {
  page: number
  limit: number
  total: number
  total_pages: number
}

/** Generic paginated list */
export interface PaginatedList<T> {
  items: Array<T>
  meta: ApiMeta
}

/** Make all properties in T deeply partial */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

/** Extract the resolved value from a Promise */
export type Await<T> = T extends Promise<infer U> ? U : T

/** Non-nullable array element */
export type NonNullableArray<T> = Array<NonNullable<T>>
