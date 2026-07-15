import { cityBudgetRecord, citySettlementRecord } from "./fukuokaCityFinance";
import {
  kitakyushuBudgetRecord,
  kitakyushuSettlementRecord,
} from "./kitakyushuFinance";

export type ComparableFiscalMetric = {
  id: string;
  label: string;
  fiscalYear: number;
  stage: "initial_budget" | "settlement";
  accountType: "general";
  fukuokaAmountYen: number;
  kitakyushuAmountYen: number;
  precisionNote: string | null;
};

function requiredAmount(amount: number | null, id: string) {
  if (amount === null) {
    throw new Error(`Missing comparison amount: ${id}`);
  }
  return amount;
}

export const cityFiscalComparison: ComparableFiscalMetric[] = [
  {
    id: "2026-initial-budget",
    label: "一般会計当初予算案",
    fiscalYear: 2026,
    stage: "initial_budget",
    accountType: "general",
    fukuokaAmountYen: requiredAmount(
      cityBudgetRecord("total_revenue").amount_yen,
      "fukuoka-2026-budget",
    ),
    kitakyushuAmountYen: requiredAmount(
      kitakyushuBudgetRecord("total_revenue").amount_yen,
      "kitakyushu-2026-budget",
    ),
    precisionNote: null,
  },
  {
    id: "2026-local-tax",
    label: "市税収入（当初予算案）",
    fiscalYear: 2026,
    stage: "initial_budget",
    accountType: "general",
    fukuokaAmountYen: requiredAmount(
      cityBudgetRecord("local_tax").amount_yen,
      "fukuoka-2026-tax",
    ),
    kitakyushuAmountYen: requiredAmount(
      kitakyushuBudgetRecord("local_tax").amount_yen,
      "kitakyushu-2026-tax",
    ),
    precisionNote: "北九州市は公式資料の億円単位の表示精度で収録。",
  },
  {
    id: "2024-settlement-revenue",
    label: "一般会計歳入決算額",
    fiscalYear: 2024,
    stage: "settlement",
    accountType: "general",
    fukuokaAmountYen: requiredAmount(
      citySettlementRecord("total_revenue").amount_yen,
      "fukuoka-2024-revenue",
    ),
    kitakyushuAmountYen: requiredAmount(
      kitakyushuSettlementRecord("total_revenue").amount_yen,
      "kitakyushu-2024-revenue",
    ),
    precisionNote: null,
  },
  {
    id: "2024-settlement-expenditure",
    label: "一般会計歳出決算額",
    fiscalYear: 2024,
    stage: "settlement",
    accountType: "general",
    fukuokaAmountYen: requiredAmount(
      citySettlementRecord("total_expenditure").amount_yen,
      "fukuoka-2024-expenditure",
    ),
    kitakyushuAmountYen: requiredAmount(
      kitakyushuSettlementRecord("total_expenditure").amount_yen,
      "kitakyushu-2024-expenditure",
    ),
    precisionNote: null,
  },
];

export const cityTaxShares = {
  fukuoka:
    (cityBudgetRecord("local_tax").amount_yen ?? 0) /
    (cityBudgetRecord("total_revenue").amount_yen ?? 1),
  kitakyushu:
    (kitakyushuBudgetRecord("local_tax").amount_yen ?? 0) /
    (kitakyushuBudgetRecord("total_revenue").amount_yen ?? 1),
};
