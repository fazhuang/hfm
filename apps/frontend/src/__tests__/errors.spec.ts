import { describe, expect, it } from 'vitest'
import { getApiErrorDetail } from '../utils/errors'

describe('getApiErrorDetail (migrated Batch 3 asset)', () => {
  it('extracts status and message from an axios-like error body', () => {
    const err = { response: { status: 422, data: { message: 'bad input' } } }
    expect(getApiErrorDetail(err)).toEqual({ status: 422, message: 'bad input' })
  })

  it('falls back to the body detail field', () => {
    const err = { response: { status: 500, data: { detail: 'boom' } } }
    expect(getApiErrorDetail(err)).toEqual({ status: 500, message: 'boom' })
  })

  it('falls back to the error message when there is no response body', () => {
    const err = { message: 'network down' }
    expect(getApiErrorDetail(err)).toEqual({ status: undefined, message: 'network down' })
  })

  it('returns an empty detail for null and non-objects', () => {
    expect(getApiErrorDetail(null)).toEqual({})
    expect(getApiErrorDetail('oops')).toEqual({})
    expect(getApiErrorDetail(undefined)).toEqual({})
  })
})
