const pillars = [
  {
    label: "Promise",
    title: "何を約束したか",
    text: "選挙公報、マニフェスト、総合計画を、評価可能な単位へ整理します。",
  },
  {
    label: "Money",
    title: "いくら使ったか",
    text: "当初予算、補正、執行、決算を区別し、事業・契約へ接続します。",
  },
  {
    label: "Result",
    title: "何が変わったか",
    text: "KPIの目標と実績を示し、因果関係を断定できない場合も明記します。",
  },
  {
    label: "Accountability",
    title: "誰がどう説明したか",
    text: "首長の説明、議会の審議、監査、訂正履歴を確認できるようにします。",
  },
];

const pilotMunicipalities = ["福岡県", "福岡市", "北九州市"];

export default function Home() {
  return (
    <main>
      <header className="siteHeader">
        <a className="brand" href="#top" aria-label="Jichi Insight ホーム">
          Jichi Insight
        </a>
        <nav aria-label="主要ナビゲーション">
          <a href="#about">目的</a>
          <a href="#pilot">初期対象</a>
          <a href="#principles">原則</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <p className="eyebrow">自治体IR・行政アカウンタビリティ基盤</p>
        <h1>
          約束・予算・実行・成果を、
          <br />
          ひとつにつなぐ。
        </h1>
        <p className="lead">
          公開されているのに、理解しにくい自治体情報を整理します。
          住民が自治体、知事・市長、議会を自分で評価するための根拠を届けます。
        </p>
        <div className="heroActions">
          <a className="primaryAction" href="#about">
            プロジェクトを知る
          </a>
          <a className="secondaryAction" href="#principles">
            評価の原則を見る
          </a>
        </div>
        <div className="status" role="status">
          <span className="statusDot" aria-hidden="true" />
          Foundation / Pre-alpha — 公開データの収録前です
        </div>
      </section>

      <section className="section" id="about">
        <div className="sectionIntro">
          <p className="eyebrow">From documents to decisions</p>
          <h2>PDFの山を、判断できる情報へ。</h2>
          <p>
            予算書、決算書、事業評価、契約、議事録、選挙公報は別々に公開されています。
            Jichi Insightは、一つの事業を起点に、それらを検証可能な形で接続します。
          </p>
        </div>
        <div className="pillarGrid">
          {pillars.map((pillar) => (
            <article className="pillarCard" key={pillar.label}>
              <p>{pillar.label}</p>
              <h3>{pillar.title}</h3>
              <span>{pillar.text}</span>
            </article>
          ))}
        </div>
      </section>

      <section className="section splitSection" id="pilot">
        <div>
          <p className="eyebrow">Pilot scope</p>
          <h2>まず、3自治体を深くつなぐ。</h2>
          <p>
            全国を浅く並べるのではなく、財政、重点事業、公約、議会まで一本につないだモデルを完成させてから拡大します。
          </p>
        </div>
        <ol className="municipalityList">
          {pilotMunicipalities.map((municipality, index) => (
            <li key={municipality}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              {municipality}
            </li>
          ))}
        </ol>
      </section>

      <section className="section principlesSection" id="principles">
        <p className="eyebrow">Trust before scale</p>
        <h2>評価より先に、根拠を見せる。</h2>
        <div className="principleGrid">
          <p>一次資料を優先し、未確認情報を推測で埋めません。</p>
          <p>事実、比較、解釈、評価を同じ文章に混ぜません。</p>
          <p>政策思想や政党ではなく、具体性、実行、成果、説明責任を見ます。</p>
          <p>データ不足なら、無理に点数を出さず「評価不能」と示します。</p>
        </div>
      </section>

      <footer>
        <p>Jichi Insight</p>
        <span>現在は基盤設計とパイロット調査を進めています。</span>
      </footer>
    </main>
  );
}
