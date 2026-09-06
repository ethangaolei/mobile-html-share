#!/usr/bin/env python3
"""Generate lessons.json: original 6 (2024 Q2, official) + 57 new (2026 Q1/Q2, AI).
Reads slice manifests for accurate durations, combines with hand-authored META."""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
existing = json.load(open(os.path.join(ROOT, "data", "lessons.json"), encoding="utf-8"))
q1 = json.load(open(os.path.join(ROOT, "data", "slices-q1-2026.json"), encoding="utf-8"))
q2 = json.load(open(os.path.join(ROOT, "data", "slices-q2-2026.json"), encoding="utf-8"))

URL = "https://www.novartis.com/investors/financial-data/quarterly-results"
SRC = {"q1-2026": ("Novartis 2026 Q1 Investor Presentation & Q&A", "2026-04"),
       "q2-2026": ("Novartis 2026 Q2 Investor Presentation & Q&A", "2026-07")}

def T(en, cn): return {"en": en, "cn": cn}

# id -> (title, titleCn, theme, speaker_mode, terms[], questions[])
META = {
 # ===== 2026 Q1 — prepared remarks D7-D18 =====
 "D7":  ("Q1 2026 opening remarks", "一季度开场", "电话会议开场与前瞻性声明", "prepared",
         [T("forward-looking statements","前瞻性声明"),T("conference call","电话会议")],
         ["这是哪一季度的电话会议？","开场强调了哪类信息风险？","接下来要讲什么？"]),
 "D8":  ("Breast cancer momentum", "乳腺癌增长动能", "品牌增长与全球上市", "prepared",
         [T("momentum","动能"),T("metastatic breast cancer","转移性乳腺癌"),T("ex-U.S. market","除美市场")],
         ["哪两个乳腺癌领域有动能？","全球上市带来什么？","除美市场表现如何？"]),
 "D9":  ("Kesimpta runway", "Kesimpta 增长空间", "Kesimpta 美国执行", "prepared",
         [T("runway","增长空间"),T("operational execution","运营执行")],
         ["Kesimpta 哪个市场表现好？","增长靠什么？","发言人对未来怎么看？"]),
 "D10": ("Growth drivers & urology", "增长驱动与泌尿科", "深化与科室扩张", "prepared",
         [T("growth driver","增长驱动"),T("urology","泌尿科"),T("expansion","扩张")],
         ["两个增长驱动是什么？","扩张到哪个科室？","为什么重要？"]),
 "D11": ("Lectio rare disease", "Lectio 罕见病", "罕见病适应症与儿科", "prepared",
         [T("rare disease","罕见病"),T("pediatric","儿科"),T("strategic exclusivity","战略独占")],
         ["Lectio 针对几个罕见病适应症？","战略独占意味着什么？","儿科为什么重要？"]),
 "D12": ("Cosentyx in HS", "Cosentyx 化脓性汗腺炎", "HS 市场份额", "prepared",
         [T("hidradenitis suppurativa","化脓性汗腺炎"),T("NBRX naive share","新患者份额")],
         ["HS 新患者份额约多少？","1 月为什么下滑？","份额趋势如何？"]),
 "D13": ("Kidney failure reduction", "肾病进展减缓", "肾病数据与 FDA 优先审评", "prepared",
         [T("kidney failure","肾衰"),T("priority review","优先审评"),T("progression","进展")],
         ["肾衰进展减少了百分之多少？","FDA 给了什么？","这意味着什么？"]),
 "D14": ("CINDU approval track", "CINDU 批准路径", "适应症扩展与申报", "prepared",
         [T("safety profile","安全性特征"),T("subtype","亚型"),T("submission","申报")],
         ["第一个亚型审批进展？","另两个亚型何时申报？","安全性如何？"]),
 "D15": ("Pipeline readouts", "管线读出", "下半年管线里程碑", "prepared",
         [T("pipeline","管线"),T("readout","数据读出")],
         ["这段讲什么主题？","下半年管线有什么？","发言人态度？"]),
 "D16": ("Sales & copay dynamics", "销售与共付", "销售下降与基数效应", "prepared",
         [T("copay","共付"),T("gross-to-net","毛转净"),T("base","基数")],
         ["销售下降百分之几？","共付下降多少？","为什么有正向毛转净？"]),
 "D17": ("Growing through LOE", "专利到期期增长", "LOE 期顶线增长", "prepared",
         [T("top line","顶线"),T("LOE","专利到期"),T("core operating income","核心营业利润")],
         ["公司在什么时期仍增长顶线？","LOE 是什么？","核心利润如何？"]),
 "D18": ("Q&A opening", "问答开场", "转入问答环节", "prepared",
         [T("open the line","开放提问")],
         ["这段标志什么环节开始？","提问交给谁？"]),
 # ===== 2026 Q1 — Q&A D19-D34 =====
 "D19": ("Q&A: HS vs MS", "问答：HS 与 MS", "适应症比较", "qa",
         [T("indication","适应症")],
         ["分析师问什么？","HS 和 MS 哪个可能更大？","管理层怎么答？"]),
 "D20": ("Growth rate outlook", "增长率展望", "增长率预期", "qa",
         [T("double-digit growth","双位数增长")],
         ["增长在什么区间？","能否回到高增长？","为什么？"]),
 "D21": ("Patient selection & CV", "患者选择与心血管", "患者分型与终点", "qa",
         [T("patient group","患者人群"),T("cardiovascular","心血管"),T("stroke","卒中")],
         ["患者分型为什么重要？","哪两个终点被比较？"]),
 "D22": ("Launch competition", "上市竞争", "竞品上市策略", "qa",
         [T("launch","上市"),T("progress","推进")],
         ["公司和对手在比什么？","上市关键是什么？"]),
 "D23": ("Deflecting competitor Q", "回避竞品问题", "管理层回避策略", "qa",
         [T("deflect","回避"),T("separate topic","另起话题")],
         ["分析师问什么被回避？","管理层怎么处理？"]),
 "D24": ("NEJM publication", "NEJM 发表", "数据发表与权威", "qa",
         [T("data set","数据集"),T("New England Journal of Medicine","新英格兰医学杂志")],
         ["数据发表在哪？","发表意味着什么？"]),
 "D25": ("ARR data discussion", "ARR 数据讨论", "年复发率数据", "qa",
         [T("ARR","年复发率")],
         ["讨论什么数据？","ARR 指什么？","为什么重复致谢？"]),
 "D26": ("Steady uptake", "稳步上量", "上量节奏预期", "qa",
         [T("steady increase","稳步增长"),T("hockey stick","曲棍球棒式")],
         ["上量是稳步还是曲棍球棒式？","为什么？"]),
 "D27": ("Longitudinal data & muscle", "纵向数据与肌肉", "长期数据与症状", "qa",
         [T("longitudinal data","纵向数据"),T("muscle manifestations","肌肉症状")],
         ["纵向数据有什么用？","最重要的症状是什么？"]),
 "D28": ("2027 readouts", "2027 数据读出", "未来里程碑", "qa",
         [T("upside","上行空间"),T("readout","数据读出")],
         ["2027 有什么？","上行空间指什么？"]),
 "D29": ("LOE extension debate", "专利到期延长讨论", "行业 LOE 动态", "qa",
         [T("LOE","专利到期"),T("end of the decade","十年末")],
         ["对手在说什么？","LOE 延长意味着什么？"]),
 "D30": ("Cautious outlook", "谨慎展望", "不过度承诺", "qa",
         [T("over-promise","过度承诺")],
         ["对什么保持谨慎？","为什么不 over-promise？"]),
 "D31": ("Pipeline studies launch", "管线研究启动", "适应症研究启动", "qa",
         [T("atopic dermatitis","特应性皮炎"),T("vitiligo","白癜风"),T("recruiting","招募中")],
         ["哪两个研究在推进？","分别什么状态？"]),
 "D32": ("Gene therapy dosing", "基因治疗剂量", "基因治疗剂量调整", "qa",
         [T("gene therapy","基因治疗"),T("dose","剂量")],
         ["哪个产品剂量在调？","底层基因治疗变了吗？"]),
 "D33": ("Phase 3 design", "III 期设计", "III 期方案确认", "qa",
         [T("Phase 3","III 期"),T("plan design","方案设计"),T("dose","剂量")],
         ["要确认什么？","哪个剂量推进？","还在讨论什么？"]),
 "D34": ("Launch & close", "上市与收尾", "IV 上市与转场", "qa",
         [T("IV","静脉")],
         ["哪个上市在推进？","这段在做什么？"]),
 # ===== 2026 Q2 — prepared remarks D35-D44 =====
 "D35": ("Q2 2026 opening", "二季度开场", "电话会议开场与前瞻性声明", "prepared",
         [T("forward-looking statements","前瞻性声明"),T("conference call","电话会议")],
         ["这是哪季度的电话会议？","开场强调什么？"]),
 "D36": ("Breast cancer leadership", "乳腺癌领导力", "乳腺癌市场份额", "prepared",
         [T("first line","一线"),T("NBRX/TRX","新处方/处方量")],
         ["哪两个乳腺癌领域领先？","NBRX 和 TRX 指什么？"]),
 "D37": ("Expansion opportunity", "扩张机会", "未满足需求与扩张", "prepared",
         [T("B-cell therapies","B 细胞疗法"),T("expansion","扩张")],
         ["多少患者用旧疗法？","扩张机会在哪？"]),
 "D38": ("Lectio 59% growth", "Lectio 59% 增长", "Lectio 强劲增长", "prepared",
         [T("strong demand","强劲需求")],
         ["Lectio 增长百分之多少？","美国增长多少？"]),
 "D39": ("Global footprint", "全球布局", "跨国批准与份额", "prepared",
         [T("approved","获批"),T("first-line NBRX leadership","一线份额领先")],
         ["在多少个除美国家获批？","日本达到什么地位？"]),
 "D40": ("Launches & approvals", "上市与批准", "区域上市与下半年批准", "prepared",
         [T("EMEA","欧洲药品管理局"),T("expansion","扩张")],
         ["上市在哪些区域推进？","下半年有什么批准？"]),
 "D41": ("DMD FDA submission", "DMD FDA 申报", "首类抗体寡核缀物申报", "prepared",
         [T("antibody oligoconjugate","抗体寡核缀物"),T("accelerated approval","加速批准"),T("DMD","杜氏肌营养不良")],
         ["哪类药首次 FDA 申报？","什么适应症？","走什么批准路径？"]),
 "D42": ("ALS & pipeline", "ALS 与管线", "下半年管线", "prepared",
         [T("ALS","肌萎缩侧索硬化"),T("second half","下半年")],
         ["哪个药在 ALS？","下半年有什么期待？"]),
 "D43": ("M&A and R&D", "并购与研发", "并购完成与内部研发", "prepared",
         [T("acquisition","并购"),T("internal R&D","内部研发")],
         ["完成哪两起并购？","同时投资什么？"]),
 "D44": ("Slide transition", "幻灯片过渡", "幻灯片跳转", "prepared",
         [T("slide","幻灯片")],
         ["这段在做什么？","为什么内容很少？"]),
 # ===== 2026 Q2 — Q&A D45-D63 =====
 "D45": ("Q&A: BofA question", "问答：美银提问", "问答开场", "qa",
         [T("Bank of America","美国银行")],
         ["第一个问题来自哪家机构？","谁在提问？"]),
 "D46": ("VHAT discussion", "VHAT 讨论", "VHAT（转写可能有误）", "qa",
         [T("VHAT","VHAT（待核对）")],
         ["这段讨论什么？","VHAT 可能是转写错误，核对逐字稿"]),
 "D47": ("Study confidence", "研究信心", "研究进展与对照", "qa",
         [T("active vs control","活性对照"),T("performing","表现")],
         ["对研究有什么信心？","active 和 control 指什么？"]),
 "D48": ("Trial rates & PCSK9", "试验比例与 PCSK9", "试验比例与竞品", "qa",
         [T("PCSK9","PCSK9 抑制剂"),T("creep up","攀升")],
         ["起始比例是多少？","PCSK9 指什么？"]),
 "D49": ("Third-party spend", "第三方支出", "支出优化", "qa",
         [T("third-party spend","第三方支出"),T("productive","有效")],
         ["第三方支出约多少？","公司在做什么？"]),
 "D50": ("Abalacimab confidence", "Abalacimab 信心", "管线信心", "qa",
         [T("abalacimab","阿巴拉西单抗"),T("confidence","信心")],
         ["分析师问哪个药？","问什么？"]),
 "D51": ("Peak sales & Europe", "峰值销售与欧洲", "峰值销售信心", "qa",
         [T("peak sales","峰值销售"),T("European Commission","欧盟委员会")],
         ["问什么信心？","刚拿到什么？"]),
 "D52": ("Share dynamics", "份额动态", "市场份额与竞争", "qa",
         [T("market share","市场份额"),T("dynamics","动态")],
         ["份额变化原因？","竞争情况？"]),
 "D53": ("IgE & Murex", "IgE 与 Murex", "IgE 靶向与新型载荷", "qa",
         [T("IgE","免疫球蛋白 E"),T("payload","载荷"),T("novel","新型")],
         ["和传统 IgE 疗法有何不同？","Murex 的特点？"]),
 "D54": ("Q&A: Deutsche Bank", "问答：德银", "问答转场", "qa",
         [T("Deutsche Bank","德意志银行")],
         ["下一个问题来自哪家？"]),
 "D55": ("Brief exchange", "简短交流", "简短问答", "qa",
         [],
         ["这段内容很少，发生了什么？","核对逐字稿确认"]),
 "D56": ("P&L & gross margin", "损益与毛利", "利润率与毛利率", "qa",
         [T("P&L","损益"),T("gross margin","毛利率")],
         ["问什么利润率？","毛利率反映什么？"]),
 "D57": ("Leqvio sales force", "Leqvio 销售队伍", "销售队伍与结局试验", "qa",
         [T("outcome trial","结局试验"),T("sales force","销售队伍")],
         ["明年有什么试验？","销售队伍用新的还是现有的？"]),
 "D58": ("Stocking dynamics", "备货动态", "备货无特定品牌", "qa",
         [T("stocking","备货"),T("across the board","全面")],
         ["备货涉及特定品牌吗？","全面还是局部？"]),
 "D59": ("Q&A: Goldman Sachs", "问答：高盛", "问答转场", "qa",
         [T("Goldman Sachs","高盛")],
         ["下一个问题来自谁？"]),
 "D60": ("Leqvio in China", "Leqvio 中国", "中国上量", "qa",
         [T("momentum","动能"),T("China","中国")],
         ["问哪个药在哪个市场？","问什么细节？"]),
 "D61": ("PCSK9 outcomes", "PCSK9 结局试验", "结局试验与意外", "qa",
         [T("outcomes trial","结局试验"),T("surprise","意外")],
         ["提到什么试验？","有什么意外？"]),
 "D62": ("CDOX & outcomes", "CDOX 与结局", "生物标志物与结局", "qa",
         [T("CDOX","CDOX（标志物）"),T("correlate","相关性")],
         ["CDOX 用来做什么？","和什么相关？"]),
 "D63": ("Rapsida access", "Rapsida 准入", "逐步推进准入", "qa",
         [T("access","准入"),T("step-by-step","逐步"),T("demand","需求")],
         ["Rapsida 推进策略是什么？","需求如何？"]),
}

def dur_str(s):
    m = int(s // 60); sec = int(round(s % 60))
    return f"{m}:{sec:02d}"

new = []
for m in q1 + q2:
    lid = m["id"]
    title, tcn, theme, sp, terms, qs = META[lid]
    src, date = SRC[m["source"]]
    speaker = "Novartis management (prepared remarks)" if sp == "prepared" else "Analyst + Novartis management (Q&A)"
    new.append({
        "id": lid, "group": m["quarter"], "title": title, "titleCn": tcn, "theme": theme,
        "source": src, "sourceUrl": URL, "date": date, "speaker": speaker,
        "duration": dur_str(m["duration"]),
        "audioFile": f"{lid}-{m['source']}.mp3", "vttFile": f"{lid}-{m['source']}.vtt",
        "transcriptMode": "ai", "terms": terms, "questions": qs,
    })

for L in existing:
    L.setdefault("group", "2024 Q2 · Week 1")

out = existing + new
with open(os.path.join(ROOT, "data", "lessons.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"lessons.json: {len(existing)} existing + {len(new)} new = {len(out)} total")
print(f"  2026 Q1: D7-D34 ({sum(1 for n in new if n['group']=='2026 Q1')})")
print(f"  2026 Q2: D35-D63 ({sum(1 for n in new if n['group']=='2026 Q2')})")
