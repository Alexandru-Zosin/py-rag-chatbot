export type ChatRequest = {
  query: string;
  k?: number;
  metadata_fields?: string[];
};

export type ChatResponse = {
  answer: string;
  sources: Array<Record<string, unknown>>;
};
