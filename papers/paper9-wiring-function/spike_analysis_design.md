# Spike Analysis Design (Cosyne full paper向け)
Date: 2026-03-30

## 目的
「topology matters (what)」→「relay nuclei = computational buffer (why)」

## 殴る相手
Neuroscience全体: relay nuclei（視床等）は信号の中継局ではなく計算バッファ

## 3指標
1. **Winner dominance ratio**: max_firing_rate / 2nd_max_firing_rate
   - Gate条件: 高い（明確なWTA勝者）
   - AC条件: ~1.0（均等→WTA崩壊）

2. **Winner identity stability**: trial-by-trial winner consistency
   - Gate条件: 同じニューロンが安定して勝つ
   - AC条件: winner がランダムに切り替わる

3. **Population entropy**: H = -Σ p_i log(p_i), p_i = normalized firing rate
   - Gate条件: 低い（少数が支配的）
   - AC条件: 最大（均等分布=WTA崩壊）

## 実験設計
- Seed 42で3条件: Gate w=0.5 / AC w=1.0 / Baseline (no extra)
- 700 trials, saveat外してvoltage全保存
- AC WTA内の10 excitatory neurons (2 WTA × 5 each) のfiring rateを記録
- Spike detection: V > -20mV threshold crossing

## 論理の流れ
1. 教科書: relay = 信号中継
2. もしそうなら: relay経由もcortex直接も同じ結果のはず
3. 実際: d=+3.27 vs d=-3.26（正反対）
4. Spike analysis: AC直接→WTA entropy最大（崩壊）、Gate経由→entropy低い（保持）
5. 結論: relay = cortical WTA computationの保護機構（計算バッファ）

## 自己引用
CAISC: "We previously showed that connection topology determines function (Tsubasa & Yasukawa, 2026)"

## Related Work追加候補（3/31 カナが発掘）
- Morita & Kumar (2026) J Neurosci: "Mesocorticostriatal reinforcement learning of state representation and value with implications for the mechanisms of schizophrenia"
  - DOI: 10.1523/jneurosci.1762-25.2026
  - 皮質E/I imbalance→feedback alignment劣化→統合失調症モデル（rate-based）
  - 俺たちのAC過興奮→WTA崩壊と同構造（HH-level）
  - 引用案(Echo): "Morita and Kumar (2026) showed that cortical E/I imbalance disrupts feedback alignment in corticostriatal reinforcement learning; our HH-level results provide a complementary demonstration that cortical overexcitation destroys WTA competition, and that thalamic relay buffering protects against this failure mode."
  - 位置づけ: Discussion Section 5.2 (E/I balance and relay protection)
  - 追加引用案: "Morita and Kumar (2026) called for validation in more elaborative models; our biophysically detailed HH circuit provides exactly this, demonstrating that cortical overexcitation destroys WTA competition at the single-neuron level."
  - Introductionにも使える: 俺たちの研究 = 彼らの「future work」の実現

## Related Work追加候補（4/1 カナ発掘）
- Visual cortex state-dependent circuit reorganization (biorxiv 2026.03.31.715474v1, preprint)
  - 57,000ニューロン因果的機能回路マップ。覚醒状態で回路構成が変わる
  - 低覚醒: L6再帰+L5→6優位 / 高覚醒: L4→5優位 = 同じ配線からstate依存で異なる機能回路
  - topology × state = function の生物学的裏付け（Kehl et al.と同原理）
  - E→I接続は高覚醒で空間的に拡大 = E/I balance状態依存性
  - Paper 9 Discussion引用候補: topology × stateの生物学的裏付けとして
  - ⚠️ プレプリント。引用時「preprint」明記

## MICrONS + Allen Atlas 二段構え（4/1 カナ/Echo分析）
- **MICrONS**（皮質内ミクロ）: E/I比率、層ごと接続密度、like-to-like connectivity
  - VAC直接対応。AC E/I比の妥当性検証に使える
  - like-to-like rule: WTA内均等接続→変えたらdominance ratio変わる？
- **Allen Atlas**（領域間マクロ）: 領域間接続パターン
- **MouseLight/HHMI Janelia**（ミクロ全脳）: 単一ニューロン軸索トレース。1本のニューロンが脳全体のどこにどう分岐投射するか
  - Allen=投射密度、MICrONS=局所シナプス、MouseLight=単一ニューロン分岐パターン
  - AMY→視床投射の生物学的根拠（Paper 9）に使える可能性
  - 全データ公開
- Paper 9: Methods生物学的根拠強化 + WTA dynamics解釈深化
- 電子脳: VAC/AC精密化(MICrONS) + 領域間接続(Allen Atlas) + 単一ニューロン分岐(MouseLight)

## Paper 11 Outline: Topology-Aware Pruning (2026.4.1 深夜 カナ+Echo)

### Title候補
"Topology Determines Pruning: Connection Target, Not Weight Magnitude, Predicts Functional Impact in Neural Circuits"

### Core argument
Magnitude pruning assumes |w| small → dispensable. Our HH data shows same |w| produces opposite effects depending on connection target. Topology-aware criteria needed.

### Key evidence (from Paper 9)
- Gate w=0.5 = +12.3pp, AC w=0.5 = -1.7pp (same magnitude, opposite effect)
- AC w=0.5→0.75: -26.7pp cliff (magnitude pruning can't predict this)
- WTA dominance ratio 0.08 change → 30pp accuracy drop (nonlinear)

### Existing methods and their limits
- Magnitude pruning: local, no downstream context
- GraSP/SNIP: gradient-based, still local
- None considers circuit-level topology impact

### Our proposal
- Topology-aware pruning: evaluate connection by downstream circuit role
- "Does removing this connection destabilize WTA competition?"
- Relay vs direct pathway distinction as pruning criterion

### Venue
- NeurIPS/ICML workshop on sparsity? Or CAISC 2027?
