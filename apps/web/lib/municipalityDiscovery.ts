import miyagiMunicipality from "../../../data/reviewed/miyagi-prefecture/municipality.json";
import sendaiMunicipality from "../../../data/reviewed/sendai-city/municipality.json";
import { miyagiFinance } from "@/lib/miyagiFinance";
import { sendaiFinance } from "@/lib/sendaiFinance";
import hyogoPrefectureMunicipality from "../../../data/reviewed/hyogo-prefecture/municipality.json";
import kobeCityMunicipality from "../../../data/reviewed/kobe-city/municipality.json";
import { hyogoFinance } from "@/lib/hyogoFinance";
import chibaPrefectureMunicipality from "../../../data/reviewed/chiba-prefecture/municipality.json";
import chibaCityMunicipality from "../../../data/reviewed/chiba-city/municipality.json";
import { chibaFinance } from "@/lib/chibaFinance";
import saitamaPrefectureMunicipality from "../../../data/reviewed/saitama-prefecture/municipality.json";
import saitamaCityMunicipality from "../../../data/reviewed/saitama-city/municipality.json";
import kawaguchiMunicipality from "../../../data/reviewed/kawaguchi-city/municipality.json";
import saitamaPrefectureBudget from "../../../data/reviewed/saitama-prefecture/fiscal_records.json";
import saitamaPrefectureSettlements from "../../../data/reviewed/saitama-prefecture/settlement_records.json";
import osakaMunicipality from "../../../data/reviewed/osaka-prefecture/municipality.json";
import kanagawaMunicipality from "../../../data/reviewed/kanagawa-prefecture/municipality.json";
import yokohamaMunicipality from "../../../data/reviewed/yokohama-city/municipality.json";
import kawasakiMunicipality from "../../../data/reviewed/kawasaki-city/municipality.json";
import osakaSettlementRecords from "../../../data/reviewed/osaka-prefecture/settlement_records.json";
import { assemblies, isAssemblySlug } from "@/lib/assemblyRegistry";
import { aichiFinance } from "@/lib/aichiFinance";
import { hokkaidoFinance } from "@/lib/hokkaidoFinance";
import { kanagawaFinance } from "@/lib/kanagawaFinance";
import { currentExecutiveTerms, promiseRecords } from "@/lib/executives";
import { fukuokaPrefectureFinance } from "@/lib/finance";
import { fukuokaCityFinance } from "@/lib/fukuokaCityFinance";
import { kitakyushuFinance } from "@/lib/kitakyushuFinance";
import { isProjectArea, projectRegistry } from "@/lib/projectRegistry";
import { loadPhase15CitySummaries } from "@/lib/phase15Cities";
import { loadGenericCityFinance } from "@/lib/genericCityFinance";

type DeepDiveKey = "fukuoka-prefecture" | "fukuoka-city" | "kitakyushu-city";

const financeByKey = {
  "fukuoka-prefecture": fukuokaPrefectureFinance,
  "fukuoka-city": fukuokaCityFinance,
  "kitakyushu-city": kitakyushuFinance,
} as const;

/**
 * Read-only availability gate. The official code is checked against the
 * Reviewed municipality record before consulting the four independent
 * registries. The key is a route identifier, never an availability shortcut.
 *
 * A municipality with no corresponding Reviewed registration receives NO
 * deep-dive links, regardless of its display name or prefecture.
 */
function hasReviewedExecutivePromises(municipalityId: string) {
  return currentExecutiveTerms.some((term) =>
    term.municipality_id === municipalityId &&
    (term.review_status === "reviewed" || term.review_status === "verified") &&
    promiseRecords.some((promise) =>
      promise.municipality_id === municipalityId &&
      promise.executive_term_id === term.id &&
      (promise.review_status === "reviewed" || promise.review_status === "verified"),
    ),
  );
}

export function municipalityDiscoveryAvailability(officialCode: string) {
  const matched = (Object.keys(financeByKey) as DeepDiveKey[]).find((key) => {
    const municipality = financeByKey[key].municipality;
    return municipality.official_code === officialCode &&
      municipality.data_status === "reviewed";
  });

  // Stage 2: Reviewed projects are available; stage 3/4 promises and assemblies are not inferred.
  // Keep key null until a dedicated municipality route or corresponding executive/assembly data is published.
  if (!matched && officialCode === miyagiMunicipality.official_code &&
    miyagiMunicipality.data_status === "reviewed") {
    const municipalityId = miyagiMunicipality.id;
    const hasProjects = projectRegistry["miyagi-prefecture"].projects.some((project) =>
      project.municipality_id === municipalityId && project.review_status === "reviewed",
    );
    const hasFinance = miyagiFinance.records.some((record) =>
      record.municipality_id === municipalityId && record.review_status === "reviewed" &&
      ((record.stage === "initial_budget" && record.account_type === "general" && record.fiscal_year === 2026) ||
       (record.stage === "settlement" && record.account_type === "ordinary" && [2022, 2023, 2024].includes(record.fiscal_year))),
    );
    const assembly = assemblies["miyagi-prefecture"];
    const hasAssembly = assembly.assembly.review_status === "reviewed" &&
      assembly.disclosure.review_status === "reviewed" &&
      assembly.assembly.municipality_id === municipalityId;
    return { key: "miyagi-prefecture", finance: hasFinance,
      promises: hasReviewedExecutivePromises(municipalityId),
      assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === sendaiMunicipality.official_code &&
    sendaiMunicipality.data_status === "reviewed") {
    const municipalityId = sendaiMunicipality.id;
    const hasProjects = projectRegistry["sendai-city"].projects.some((project) =>
      project.municipality_id === municipalityId && project.review_status === "reviewed",
    );
    const hasFinance = sendaiFinance.records.some((record) =>
      record.municipality_id === municipalityId && record.review_status === "reviewed" &&
      record.stage === "initial_budget" && record.account_type === "general" &&
      record.fiscal_year === 2026,
    );
    const assembly = assemblies["sendai-city"];
    const hasAssembly = assembly.assembly.review_status === "reviewed" &&
      assembly.disclosure.review_status === "reviewed" &&
      assembly.assembly.municipality_id === municipalityId;
    return { key: "sendai-city", finance: hasFinance,
      promises: hasReviewedExecutivePromises(municipalityId),
      assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === hyogoPrefectureMunicipality.official_code &&
    hyogoPrefectureMunicipality.data_status === "reviewed") {
    const municipalityId = hyogoPrefectureMunicipality.id;
    const hasProjects = projectRegistry["hyogo-prefecture"].projects.some((project) =>
      project.municipality_id === municipalityId && project.review_status === "reviewed",
    );
    const hasFinance = hyogoFinance.records.some((record) =>
      record.municipality_id === municipalityId && record.review_status === "reviewed" &&
      ((record.stage === "initial_budget" && record.account_type === "general" && record.fiscal_year === 2026) ||
       (record.stage === "settlement" && record.account_type === "ordinary" && [2022, 2023, 2024].includes(record.fiscal_year))),
    );
    const entry = assemblies["hyogo-prefecture"];
    const hasAssembly = entry.assembly.review_status === "reviewed" &&
      entry.disclosure.review_status === "reviewed" &&
      entry.assembly.id.startsWith(municipalityId + "-assembly-");
    return {
      key: "hyogo-prefecture", finance: hasFinance,
      promises: hasReviewedExecutivePromises(municipalityId),
      assembly: hasAssembly, projects: hasProjects,
    };
  }

  if (!matched && officialCode === kobeCityMunicipality.official_code &&
    kobeCityMunicipality.data_status === "reviewed") {
    const municipalityId = kobeCityMunicipality.id;
    const hasProjects = projectRegistry["kobe-city"].projects.some((project) =>
      project.municipality_id === municipalityId && project.review_status === "reviewed",
    );
    const entry = assemblies["kobe-city"];
    const hasAssembly = entry.assembly.review_status === "reviewed" &&
      entry.disclosure.review_status === "reviewed" &&
      entry.assembly.id.startsWith(municipalityId + "-assembly-");
    return {
      key: "kobe-city", finance: loadGenericCityFinance("kobe-city") !== null,
      promises: hasReviewedExecutivePromises(municipalityId),
      assembly: hasAssembly, projects: hasProjects,
    };
  }

  if (!matched && officialCode === saitamaPrefectureMunicipality.official_code && saitamaPrefectureMunicipality.data_status === "reviewed") {
    const hasProjects = projectRegistry["saitama-prefecture"].projects.some(project => project.municipality_id === saitamaPrefectureMunicipality.id && project.review_status === "reviewed");
    const hasFinance = [...saitamaPrefectureBudget, ...saitamaPrefectureSettlements].some(record => record.municipality_id === saitamaPrefectureMunicipality.id && record.review_status === "reviewed" && ((record.stage === "initial_budget" && record.fiscal_year === 2026) || (record.stage === "settlement" && [2022, 2023, 2024].includes(record.fiscal_year))));
    const hasPromises = hasReviewedExecutivePromises(saitamaPrefectureMunicipality.id);
    const entry = assemblies["saitama-prefecture"];
    const hasAssembly = entry.assembly.review_status === "reviewed" && entry.disclosure.review_status === "reviewed" && entry.assembly.id.startsWith(saitamaPrefectureMunicipality.id + "-assembly-");
    return { key: "saitama-prefecture", finance: hasFinance, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === saitamaCityMunicipality.official_code && saitamaCityMunicipality.data_status === "reviewed") {
    const hasProjects = projectRegistry["saitama-city"].projects.some(project => project.municipality_id === saitamaCityMunicipality.id && project.review_status === "reviewed");
    const hasFinance = loadGenericCityFinance("saitama-city") !== null;
    const hasPromises = hasReviewedExecutivePromises(saitamaCityMunicipality.id);
    const entry = assemblies["saitama-city"];
    const hasAssembly = entry.assembly.review_status === "reviewed" && entry.disclosure.review_status === "reviewed" && entry.assembly.id.startsWith(saitamaCityMunicipality.id + "-assembly-");
    return { key: "saitama-city", finance: hasFinance, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === kawaguchiMunicipality.official_code && kawaguchiMunicipality.data_status === "reviewed") {
    const hasProjects = projectRegistry["kawaguchi-city"].projects.some(project => project.municipality_id === kawaguchiMunicipality.id && project.review_status === "reviewed");
    const hasFinance = loadGenericCityFinance("kawaguchi-city") !== null;
    const hasPromises = hasReviewedExecutivePromises(kawaguchiMunicipality.id);
    const entry = assemblies["kawaguchi-city"];
    const hasAssembly = entry.assembly.review_status === "reviewed" && entry.disclosure.review_status === "reviewed" && entry.assembly.id.startsWith(kawaguchiMunicipality.id + "-assembly-");
    return { key: "kawaguchi-city", finance: hasFinance, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === kanagawaMunicipality.official_code &&
    kanagawaMunicipality.data_status === "reviewed") {
    const hasProjects = projectRegistry["kanagawa-prefecture"].projects.some((project) =>
      project.review_status === "reviewed" &&
      project.municipality_id === kanagawaMunicipality.id,
    );
    const hasFinance = kanagawaFinance.records.some((record) =>
      record.municipality_id === kanagawaMunicipality.id &&
      record.review_status === "reviewed" &&
      ((record.stage === "initial_budget" && record.account_type === "general" && record.fiscal_year === 2026) ||
        (record.stage === "settlement" && record.account_type === "ordinary" && [2022, 2023, 2024].includes(record.fiscal_year))),
    );
    const hasPromises = hasReviewedExecutivePromises(kanagawaMunicipality.id);
    const hasAssembly = assemblies["kanagawa-prefecture"].assembly.review_status === "reviewed" &&
      assemblies["kanagawa-prefecture"].disclosure.review_status === "reviewed";
    return { key: "kanagawa-prefecture", finance: hasFinance, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === yokohamaMunicipality.official_code &&
    yokohamaMunicipality.data_status === "reviewed") {
    const hasProjects = projectRegistry["yokohama-city"].projects.some((project) =>
      project.review_status === "reviewed" &&
      project.municipality_id === yokohamaMunicipality.id,
    );
    // Stage three promises and stage four assembly gates are independent Reviewed registrations.
    const hasPromises = hasReviewedExecutivePromises(yokohamaMunicipality.id);
    const hasAssembly = assemblies["yokohama-city"].assembly.review_status === "reviewed" &&
      assemblies["yokohama-city"].disclosure.review_status === "reviewed";
    return { key: "yokohama-city", finance: false, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === kawasakiMunicipality.official_code &&
    kawasakiMunicipality.data_status === "reviewed") {
    const hasProjects = projectRegistry["kawasaki-city"].projects.some((project) =>
      project.review_status === "reviewed" &&
      project.municipality_id === kawasakiMunicipality.id,
    );
    // Stage three promises and stage four assembly gates are independent Reviewed registrations.
    const hasPromises = hasReviewedExecutivePromises(kawasakiMunicipality.id);
    const hasAssembly = assemblies["kawasaki-city"].assembly.review_status === "reviewed" &&
      assemblies["kawasaki-city"].disclosure.review_status === "reviewed";
    return { key: "kawasaki-city", finance: false, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === hokkaidoFinance.municipality.official_code &&
    hokkaidoFinance.municipality.data_status === "reviewed") {
    const hasReviewedSettlement = hokkaidoFinance.records.some((record) =>
      record.municipality_id === hokkaidoFinance.municipality.id &&
      record.review_status === "reviewed" &&
      record.stage === "settlement" &&
      record.account_type === "ordinary" &&
      [2022, 2023, 2024].includes(record.fiscal_year),
    );
    // Independent Reviewed data gates: assembly stays closed until stage four.
    const hasProjects = projectRegistry["hokkaido-prefecture"].projects.some((project) =>
      project.review_status === "reviewed" &&
      project.municipality_id === hokkaidoFinance.municipality.id,
    );
    const hasPromises = currentExecutiveTerms.some((term) =>
      term.municipality_id === hokkaidoFinance.municipality.id &&
      (term.review_status === "reviewed" || term.review_status === "verified") &&
      promiseRecords.some((promise) =>
        promise.executive_term_id === term.id &&
        promise.municipality_id === term.municipality_id &&
        (promise.review_status === "reviewed" || promise.review_status === "verified"),
      ),
    );
    return { key: "hokkaido-prefecture", finance: hasReviewedSettlement, promises: hasPromises, assembly: false, projects: hasProjects };
  }


  if (!matched && officialCode === osakaMunicipality.official_code &&
    osakaMunicipality.data_status === "reviewed") {
    const hasFinance = osakaSettlementRecords.some((record) =>
      record.municipality_id === osakaMunicipality.id &&
      record.review_status === "reviewed" &&
      record.stage === "settlement" &&
      record.account_type === "ordinary",
    );
    const hasProjects = projectRegistry["osaka-prefecture"].projects.some((project) =>
      project.municipality_id === osakaMunicipality.id &&
      project.review_status === "reviewed",
    );
    const hasPromises = currentExecutiveTerms.some((term) =>
      term.municipality_id === osakaMunicipality.id &&
      (term.review_status === "reviewed" || term.review_status === "verified") &&
      promiseRecords.some((promise) =>
        promise.executive_term_id === term.id &&
        promise.municipality_id === osakaMunicipality.id &&
        (promise.review_status === "reviewed" || promise.review_status === "verified"),
      ),
    );
    const hasAssembly = assemblies["osaka-prefecture"].assembly.review_status === "reviewed" &&
      assemblies["osaka-prefecture"].disclosure.review_status === "reviewed";
    return { key: "osaka-prefecture", finance: hasFinance, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched && officialCode === aichiFinance.municipality.official_code &&
    aichiFinance.municipality.data_status === "reviewed") {
    const hasReviewedSettlement = aichiFinance.records.some((record) =>
      record.municipality_id === aichiFinance.municipality.id &&
      record.review_status === "reviewed" &&
      record.stage === "settlement" &&
      record.account_type === "ordinary" &&
      [2022, 2023, 2024].includes(record.fiscal_year),
    );
    // Only reviewed projects in the matching prefecture activate this link.
    // Governor promises and assembly records remain unregistered.
    const hasProjects = projectRegistry["aichi-prefecture"].projects.some((project) =>
      project.review_status === "reviewed" &&
      project.municipality_id === aichiFinance.municipality.id,
    );
    const hasAssembly = assemblies["aichi-prefecture"].assembly.review_status === "reviewed" &&
      assemblies["aichi-prefecture"].disclosure.review_status === "reviewed";
    const hasPromises = currentExecutiveTerms.some((term) =>
      term.municipality_id === aichiFinance.municipality.id &&
      (term.review_status === "reviewed" || term.review_status === "verified") &&
      promiseRecords.some((promise) =>
        promise.executive_term_id === term.id &&
        (promise.review_status === "reviewed" || promise.review_status === "verified"),
      ),
    );
    return { key: hasAssembly ? "aichi-prefecture" : null, finance: hasReviewedSettlement, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (officialCode === chibaPrefectureMunicipality.official_code &&
    chibaPrefectureMunicipality.data_status === "reviewed") {
    const hasProjects = projectRegistry["chiba-prefecture"].projects.some((project) =>
      project.review_status === "reviewed" && project.municipality_id === chibaPrefectureMunicipality.id,
    );
    const hasPromises = hasReviewedExecutivePromises(chibaPrefectureMunicipality.id);
    const entry = assemblies["chiba-prefecture"];
    const hasAssembly = entry.assembly.review_status === "reviewed" &&
      entry.disclosure.review_status === "reviewed" &&
      entry.assembly.id.startsWith(chibaPrefectureMunicipality.id + "-assembly-");
    const hasFinance = chibaFinance.records.some((record) =>
      record.municipality_id === chibaPrefectureMunicipality.id && record.review_status === "reviewed",
    );
    return { key: "chiba-prefecture", finance: hasFinance, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (officialCode === chibaCityMunicipality.official_code &&
    chibaCityMunicipality.data_status === "reviewed") {
    const hasProjects = projectRegistry["chiba-city"].projects.some((project) =>
      project.review_status === "reviewed" && project.municipality_id === chibaCityMunicipality.id,
    );
    const hasPromises = hasReviewedExecutivePromises(chibaCityMunicipality.id);
    const entry = assemblies["chiba-city"];
    const hasAssembly = entry.assembly.review_status === "reviewed" &&
      entry.disclosure.review_status === "reviewed" &&
      entry.assembly.id.startsWith(chibaCityMunicipality.id + "-assembly-");
    return { key: "chiba-city", finance: false, promises: hasPromises, assembly: hasAssembly, projects: hasProjects };
  }

  if (!matched) {
    // The Phase 15 city identity is checked by official code and Reviewed completion.
    // Finance, promises, assembly and projects then use independent data-backed gates;
    // in particular Sapporo/Asahikawa projects must match the official municipality ID.
    const city = loadPhase15CitySummaries().find((item) => item.officialCode === officialCode);
    const hasFinance = city ? loadGenericCityFinance(city.slug) !== null : false;
    const hasProjects = city && isProjectArea(city.slug)
      ? projectRegistry[city.slug].projects.some((project) =>
        project.review_status === "reviewed" &&
        project.municipality_id === `jp-local-${officialCode}`,
      )
      : false;
    // Activate the independent gates only when official-code identity and the
    // relevant Reviewed records are both present. Toyota has no manifesto.
    const hasAssembly = Boolean(city && isAssemblySlug(city.slug) &&
      assemblies[city.slug].assembly.id.startsWith(`jp-local-${officialCode}-assembly-`) &&
      assemblies[city.slug].assembly.review_status === "reviewed" &&
      assemblies[city.slug].disclosure.review_status === "reviewed");
    const hasPromises = Boolean(city && currentExecutiveTerms.some((term) =>
      term.municipality_id === `jp-local-${officialCode}` &&
      (term.review_status === "reviewed" || term.review_status === "verified") &&
      promiseRecords.some((promise) =>
        promise.municipality_id === term.municipality_id &&
        promise.executive_term_id === term.id &&
        (promise.review_status === "reviewed" || promise.review_status === "verified"),
      ),
    ));
    if (hasAssembly || hasPromises) {
      return { finance: hasFinance, promises: hasPromises, assembly: hasAssembly, projects: Boolean(hasProjects), key: city?.slug ?? null };
    }
    if (hasProjects) {
      return { finance: hasFinance, promises: false, assembly: false, projects: true, key: null };
    }
    return { finance: hasFinance, promises: false, assembly: false, projects: false, key: null };
  }

  const municipality = financeByKey[matched].municipality;
  const registeredFinance = financeByKey[matched].records.some(
    (record) => record.review_status === "reviewed" &&
      record.stage === "settlement" && record.account_type === "ordinary" &&
      [2022, 2023, 2024].includes(record.fiscal_year),
  );
  const reviewedTerms = currentExecutiveTerms.filter(
    (term) => term.municipality_id === municipality.id &&
      (term.review_status === "reviewed" || term.review_status === "verified"),
  );
  const registeredPromises = reviewedTerms.some((term) =>
    promiseRecords.some((promise) =>
      promise.executive_term_id === term.id &&
      promise.municipality_id === municipality.id &&
      (promise.review_status === "reviewed" || promise.review_status === "verified"),
    ),
  );
  const assembly = assemblies[matched];
  const registeredAssembly =
    assembly.assembly.review_status === "reviewed" &&
    assembly.disclosure.review_status === "reviewed";
  const registeredProjects = projectRegistry[matched].projects.some(
    (project) => project.review_status === "reviewed",
  );

  return {
    key: matched,
    finance: registeredFinance,
    promises: registeredPromises,
    assembly: registeredAssembly,
    projects: registeredProjects,
  };
}
