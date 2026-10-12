/** Resolved before acceptance and kept for retries; never an LLM sampling option. */
export function imageSeeds(count: number): number[] {
  return Array.from(crypto.getRandomValues(new Uint32Array(count)));
}

export function validImageSeed(value: string): boolean {
  return /^\d+$/.test(value) && Number(value) <= 4294967295;
}
