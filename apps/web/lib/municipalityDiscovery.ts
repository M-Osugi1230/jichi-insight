import { assemblies, isAssemblySlug } from "@/lib/assemblyRegistry";
import { aichiFinance } from "@/lib/aichiFinance";
import { hokkaidoFinance } from "@/lib/hokkaidoFinance";
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
export function municipalityDiscoveryAvailability(officialCode: string) {
  const matched = (Object.keys(financeByKey) as DeepDiveKey[]).find((key) => {
    const municipality = financeByKey[key].municipality;
    return municipality.official_code === officialCode &&
      municipality.data_status === "reviewed";
  });

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
