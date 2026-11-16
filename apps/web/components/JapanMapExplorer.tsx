"use client";

import Link from "next/link";
import { useMemo, useState, type CSSProperties, type KeyboardEvent } from "react";

import { japanMapPaths } from "@/lib/japanMapPaths";

import styles from "./JapanMapExplorer.module.css";

export type MapPrefecture = {
  code: string;
  name: string;
  region: string;
  href: string;
};

export type MapCity = {
  slug: string;
  name: string;
  prefecture: string;
  href: string;
};

type Props = {
  prefectures: MapPrefecture[];
  cities: MapCity[];
};

const regions = [
  "北海道",
  "東北",
  "関東",
  "中部",
  "近畿",
  "中国",
  "四国",
  "九州・沖縄",
] as const;

const colors: Record<string, string> = {
  北海道: "#b8d9d7",
  東北: "#b8d2e7",
  関東: "#e4c79d",
  中部: "#b9d7bc",
  近畿: "#c7c0df",
  中国: "#e4c5c6",
  四国: "#e9d5a8",
  "九州・沖縄": "#acd7ce",
};

export function JapanMapExplorer({ prefectures, cities }: Props) {
  const [region, setRegion] = useState<string | null>(null);
  const [selectedCode, setSelectedCode] = useState<string | null>(null);

  const prefectureByCode = useMemo(
    () => new Map(prefectures.map((item) => [item.code, item])),
    [prefectures],
  );

  const selected = selectedCode ? prefectureByCode.get(selectedCode) : null;
  const regionPrefectures = region
    ? prefectures.filter((item) => item.region === region)
    : [];
  const reviewedCities = selected
    ? cities.filter((item) => item.prefecture === selected.name)
    : [];

  function selectRegion(nextRegion: string) {
    setRegion(nextRegion);
    setSelectedCode(null);
  }

  function selectPrefecture(code: string) {
    const prefecture = prefectureByCode.get(code);
    if (!prefecture) return;
    setRegion(prefecture.region);
    setSelectedCode(code);
  }

  function onMapKeyDown(event: KeyboardEvent<SVGPathElement>, code: string) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      selectPrefecture(code);
    }
  }

  return (
    <section className={styles.explorer} aria-labelledby="japan-map-title">
      <div className={styles.intro}>
        <div>
          <p className={styles.eyebrow}>JICHI INSIGHT / FIND YOUR AREA</p>
          <h1 id="japan-map-title">地図から、まちを見つける。</h1>
          <p className={styles.lead}>
            地方・都道府県を選んで、政策や予算を調べる。
          </p>
        </div>
        <Link className={styles.listLink} href="/municipalities#prefectures">
          47都道府県の一覧 <span aria-hidden="true">↗</span>
        </Link>
      </div>

      <div className={styles.workspace}>
        <div className={styles.mapCard}>
          <div className={styles.mapHeading}>
            <span><span className={styles.mapDot} aria-hidden="true" /> 日本全国</span>
            <span>47都道府県</span>
          </div>
          <svg
            className={styles.japanMap}
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 2000 2000"
            role="group"
            aria-label="都道府県を選択する日本地図"
          >
            {japanMapPaths.map(({ code, name, d }) => {
              const prefecture = prefectureByCode.get(code);
              if (!prefecture) return null;
              const isSelected = selectedCode === code;
              const isDimmed = Boolean(region && prefecture.region !== region);
              const colorStyle = {
                "--map-color": colors[prefecture.region] ?? "#b9d9d2",
              } as CSSProperties;

              return (
                <path
                  key={code}
                  d={d}
                  className={[
                    styles.prefecture,
                    isSelected ? styles.selected : "",
                    isDimmed ? styles.dimmed : "",
                  ].filter(Boolean).join(" ")}
                  style={colorStyle}
                  onClick={() => selectPrefecture(code)}
                  onKeyDown={(event) => onMapKeyDown(event, code)}
                  role="button"
                  tabIndex={0}
                  aria-label={`${name}を選択`}
                  aria-pressed={isSelected}
                >
                  <title>{name}</title>
                </path>
              );
            })}
          </svg>
          <p className={styles.mapHint}>
            地図をタップ。または右側から地方を選択。
          </p>
        </div>

        <div className={styles.selectCard}>
          <div className={styles.selectTop}>
            <span className={styles.step}>01</span>
            <div>
              <h2>地方を選択</h2>
              <p>8つの地方から探せます</p>
            </div>
          </div>

          <div className={styles.regionGrid} aria-label="地方の一覧">
            {regions.map((item) => (
              <button
                type="button"
                key={item}
                className={region === item ? styles.activeRegion : ""}
                aria-pressed={region === item}
                onClick={() => selectRegion(item)}
              >
                <span className={styles.regionMark} style={{ backgroundColor: colors[item] }} />
                {item}
              </button>
            ))}
          </div>

          <div className={styles.detail} aria-live="polite" aria-atomic="false">
            {region ? (
              <>
                <div className={styles.detailHeading}>
                  <span className={styles.step}>02</span>
                  <div>
                    <h3>{region}の都道府県</h3>
                    <p>{regionPrefectures.length}都道府県</p>
                  </div>
                </div>
                <div className={styles.prefectureGrid}>
                  {regionPrefectures.map((item) => (
                    <button
                      type="button"
                      key={item.code}
                      aria-pressed={selectedCode === item.code}
                      className={selectedCode === item.code ? styles.activePrefecture : ""}
                      onClick={() => selectPrefecture(item.code)}
                    >
                      {item.name}
                    </button>
                  ))}
                </div>
                {selected ? (
                  <div className={styles.selection}>
                    <div className={styles.selectionHeader}>
                      <span className={styles.selectionEyebrow}>選択中の自治体</span>
                      <h4>{selected.name}</h4>
                    </div>
                    <Link className={styles.primaryAction} href={selected.href}>
                      {selected.name}の情報を見る <span aria-hidden="true">→</span>
                    </Link>
                    <div className={styles.cities}>
                      <h5>詳細レビュー済みの市</h5>
                      {reviewedCities.length ? (
                        <ul>
                          {reviewedCities.map((city) => (
                            <li key={city.slug}>
                              <Link href={city.href}>
                                <span>{city.name}</span><span aria-hidden="true">→</span>
                              </Link>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p>この都道府県では、市の詳細レビュー済みページはまだありません。</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className={styles.prompt}>都道府県を選ぶと、公開中の市の情報も表示します。</p>
                )}
              </>
            ) : (
              <div className={styles.emptyPanel}>
                <span aria-hidden="true">↖</span>
                <strong>気になる地域を選んでください</strong>
                <p>日本地図から直接選ぶこともできます。</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className={styles.footer}>
        <span><span className={styles.verifiedDot} aria-hidden="true" /> 47都道府県の政策計画を掲載</span>
        <span>市の詳細は一次資料レビュー完了分のみ公開</span>
        <Link href="/review-progress">公開範囲を見る →</Link>
      </div>
    </section>
  );
}
