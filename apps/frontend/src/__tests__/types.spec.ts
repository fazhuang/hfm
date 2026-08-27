import { describe, expectTypeOf, it } from 'vitest'
import type {
  ApiMeta,
  ApiResponse,
  Await,
  DeepPartial,
  NonNullableArray,
  PaginatedList,
} from '../types/api'

describe('shared API type contracts (migrated Batch 2 asset)', () => {
  it('ApiResponse carries data and pagination meta', () => {
    const r: ApiResponse<{ id: string }> = {
      data: { id: '1' },
      meta: { page: 1, limit: 20, total: 1, total_pages: 1 },
    }
    expectTypeOf(r.data.id).toBeString()
    expectTypeOf(r.meta.total_pages).toBeNumber()
  })

  it('PaginatedList items are arrays of T', () => {
    expectTypeOf<PaginatedList<number>['items']>().toEqualTypeOf<number[]>()
    expectTypeOf<ApiMeta['limit']>().toBeNumber()
  })

  it('Await resolves the promise value type', () => {
    expectTypeOf<Await<Promise<string>>>().toEqualTypeOf<string>()
  })

  it('DeepPartial makes nested properties optional', () => {
    type Input = { a: string; nested: { b: number } }
    type Expected = { a?: string; nested?: { b?: number } }
    expectTypeOf<DeepPartial<Input>>().toEqualTypeOf<Expected>()
  })

  it('NonNullableArray strips null/undefined from elements', () => {
    expectTypeOf<NonNullableArray<string | null | undefined>>().toEqualTypeOf<string[]>()
  })
})
