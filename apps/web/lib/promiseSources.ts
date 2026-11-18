import executiveCatalog from "../../../data/catalog/executive_sources.json";
import { sourceCatalog } from "./catalog";
import type { SourceRecord } from "./catalog";
const sources:SourceRecord[] = [...sourceCatalog,...(executiveCatalog.records as SourceRecord[])];
export function promiseSourceDetails(ids:string[]) {
  return ids.map(id=>{
    const source=sources.find(s=>s.id===id);
    return {id,title:source?.title ?? id,url:source?.url ?? null,
      review:source ? `出典レビュー：${source.review_status}` : "出典カタログ未接続",
      confidence:source ? `確信度：${source.confidence}` : "確信度未登録"};
  });
}
