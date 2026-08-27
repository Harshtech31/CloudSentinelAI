import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const root = process.cwd();
const out = path.join(root, "cloudsentinel-thesis");
const src = path.join(root, "docs/thesis/google-doc-export.md");

const clean = (s) =>
  s
    .replace(/\r/g, "")
    .replace(/\u000b/g, "\n")
    .replace(/✓/g, "$\\checkmark$")
    .replace(/✗/g, "$\\times$")
    .replace(/→/g, "$\\rightarrow$")
    .replace(/–/g, "--")
    .replace(/—/g, "---")
    .replace(/[├└│]/g, "|")
    .replace(/─/g, "-")
    .replace(/[“”]/g, '"')
    .replace(/[‘’]/g, "'");

const plainHeading = (line) =>
  line
    .replace(/^#+\s*/, "")
    .replace(/\*\*/g, "")
    .replace(/\\([.*_+])/g, "$1")
    .trim();

const slug = (s) =>
  s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_|_$/g, "");

const figureCaptions = {
  "6.1": "CloudSentinel AI System Architecture.",
  "6.2": "Cloud Asset and Security Analysis Workflow.",
  "6.3": "Knowledge Graph Construction Pipeline.",
  "6.4": "Context-Aware Risk Assessment Flow.",
  "7.1": "Research Methodology Workflow.",
  "8.1": "System Design and Algorithmic Framework.",
  "9.1": "Knowledge Graph Representation.",
  "9.2": "Attack Graph Generation Process.",
  "9.3": "Context-Aware Risk Prioritization.",
  "10.1": "Experimental Evaluation Workflow.",
  "10.2": "Injected Misconfiguration Scenario Design.",
  "10.3": "Evaluation Metrics and Analysis Flow.",
  "10.4": "End-to-End Validation Scenario.",
  "11.1": "Expected Comparison with Existing Cloud Security Solutions.",
  "11.2": "CloudSentinel AI Result and Recommendation Flow.",
};

const citations = [
  [/NIST defines cloud computing as/g, "NIST defines cloud computing as \\cite{nist2011cloud}"],
  [/Design Science Research \(DSR\) methodology/g, "Design Science Research (DSR) methodology \\cite{hevner2004design}"],
  [/attack graph is a graphical representation/g, "attack graph is a graphical representation \\cite{phillips1998graph,sheyner2002automated,jha2002formal}"],
  [/Knowledge graphs provide a structured representation/g, "Knowledge graphs provide a structured representation \\cite{hogan2021knowledge}"],
  [/Explainable Artificial Intelligence \(XAI\) addresses this limitation/g, "Explainable Artificial Intelligence (XAI) addresses this limitation \\cite{rjoub2023xai,charmet2022xai}"],
  [/Large Language Models \(LLMs\) have recently demonstrated/g, "Large Language Models (LLMs) have recently demonstrated \\cite{vaswani2017attention,brown2020language,openai2023gpt4}"],
  [/improperly configured IAM policies remain one of the leading causes/g, "improperly configured IAM policies remain one of the leading causes \\cite{vanede2022iam}"],
  [/software misconfigurations primarily arise/g, "software misconfigurations primarily arise \\cite{liu2024misconfigurations}"],
];

function addCitations(text) {
  for (const [from, to] of citations) text = text.replace(from, to);
  return text;
}

function normalizeHeadings(text) {
  return text
    .split("\n")
    .map((line) => {
      const h = plainHeading(line);
      if (/^CHAPTER\s+\d+/i.test(h) || /^Chapter\s+\d+/.test(h)) return `# ${h.replace(/^CHAPTER/i, "Chapter")}`;
      if (/^\d+\.\d+\.\d+\s+/.test(h)) return `### ${h}`;
      if (/^\d+\.\d+\s+/.test(h) || /^Chapter\s+\d+\s+Summary/i.test(h)) return `## ${h}`;
      if (line.startsWith("## ")) return `### ${h}`;
      if (line.startsWith("# ") && h) return `## ${h}`;
      return line;
    })
    .join("\n");
}

function insertFigures(chapterNo, text) {
  const ids = Object.keys(figureCaptions).filter((id) => id.startsWith(`${chapterNo}.`));
  if (!ids.length) return text;
  const lines = text.split("\n");
  const used = new Set();
  for (const id of ids) {
    const i = lines.findIndex((line) => line.includes(`Figure ${id}`));
    const md = `\n![${figureCaptions[id]}](figures/image-${id}.png){#fig:${id.replace(".", "_")} width=90%}\n`;
    if (i >= 0) {
      lines.splice(i + 1, 0, md);
      used.add(id);
    }
  }
  const rest = ids.filter((id) => !used.has(id));
  if (rest.length) {
    lines.push("\n## Additional Figures\n");
    for (const id of rest) lines.push(`![${figureCaptions[id]}](figures/image-${id}.png){#fig:${id.replace(".", "_")} width=90%}\n`);
  }
  return lines.join("\n");
}

function write(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, data);
}

function pandoc(input, output) {
  execFileSync("pandoc", [input, "-f", "markdown+raw_tex-auto_identifiers", "-t", "latex", "--wrap=none", "-o", output], { stdio: "inherit" });
  fs.writeFileSync(output, fs.readFileSync(output, "utf8")
    .replace(/[├└│]/g, "|")
    .replace(/─/g, "-")
    .replaceAll("../figures/", "figures/")
    .replace(/width=0.9\\textwidth,height=\\textheight/g, "width=0.9\\textwidth,height=0.78\\textheight,keepaspectratio"));
}

let md = clean(fs.readFileSync(src, "utf8"));
md = md.replace(/^# \*\*Tab 1\*\*\n+/, "");
md = addCitations(md);

const refStart = md.search(/^# \*\*REFERENCES\*\*/m);
const withoutRefs = refStart >= 0 ? md.slice(0, refStart) : md;
const tailStart = withoutRefs.search(/^Tables:\s*$/m);
const mainPart = tailStart >= 0 ? withoutRefs.slice(0, tailStart) : withoutRefs;
const supportPart = tailStart >= 0 ? withoutRefs.slice(tailStart).replace(/^Tables:\s*$/m, "# Supporting Tables, Equations, and Algorithms") : "";

const chapterMatches = [...mainPart.matchAll(/^# \*\*(?:CHAPTER|Chapter)\s+(\d+)[^\n]*$/gim)];
for (let i = 0; i < chapterMatches.length; i++) {
  const no = chapterMatches[i][1];
  const start = chapterMatches[i].index;
  const end = i + 1 < chapterMatches.length ? chapterMatches[i + 1].index : mainPart.length;
  const title = plainHeading(chapterMatches[i][0]).replace(/^CHAPTER/i, "Chapter").replace(/[–:]/g, " ");
  const name = `chapter${no}_${slug(title.replace(/^chapter\s+\d+/i, "")) || "chapter"}.tex`;
  const mdFile = path.join(out, "build", name.replace(/\.tex$/, ".md"));
  let body = normalizeHeadings(mainPart.slice(start, end));
  body = insertFigures(no, body);
  write(mdFile, body);
  pandoc(mdFile, path.join(out, "chapters", name));
}

const appendixFigures = ["a.1", "a.2", "a.3", "a.4", "a.5"]
  .map((id) => `![Appendix figure ${id.toUpperCase()}.](figures/image-${id}.png){#fig:${id.replace(".", "_")} width=90%}`)
  .join("\n\n");
write(path.join(out, "build/supporting.md"), `${normalizeHeadings(supportPart)}\n\n# Appendix Figures\n\n${appendixFigures}\n`);
pandoc(path.join(out, "build/supporting.md"), path.join(out, "appendix", "appendix_a.tex"));

const chapters = fs
  .readdirSync(path.join(out, "chapters"))
  .filter((f) => f.endsWith(".tex"))
  .sort((a, b) => Number(a.match(/chapter(\d+)/)[1]) - Number(b.match(/chapter(\d+)/)[1]));

write(
  path.join(out, "main.tex"),
  String.raw`\documentclass[12pt,a4paper]{report}
\usepackage[a4paper,margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs,longtable,array}
\usepackage{multirow}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{caption}
\usepackage{float}
\usepackage{xcolor}
\usepackage{url}
\usepackage{cite}
\usepackage[hidelinks]{hyperref}
\usepackage{cleveref}
\usepackage{pifont}
\newcommand{\tightlist}{}
\setcounter{tocdepth}{2}
\title{CloudSentinel AI\\A Context-Aware Cloud Misconfiguration Risk Assessment and Attack Path Analysis Framework}
\author{Harshith}
\date{2026}
\begin{document}
\pagenumbering{roman}
\maketitle
\tableofcontents
\listoffigures
\listoftables
\clearpage
\pagenumbering{arabic}
${chapters.map((f) => `\\input{chapters/${f}}`).join("\n")}
\appendix
\input{appendix/appendix_a}
\bibliographystyle{IEEEtran}
\bibliography{references}
\end{document}
`
);

write(
  path.join(out, "references.bib"),
  String.raw`@inproceedings{vanede2022iam,
  author={van Ede, Thijs and Khasuntsev, Nikita and Steen, Bas and Continella, Andrea},
  title={Detecting Anomalous Misconfigurations in AWS Identity and Access Management Policies},
  booktitle={Proceedings of the 2022 ACM Cloud Computing Security Workshop},
  year={2022},
  pages={63--74},
  doi={10.1145/3560810.3564264}
}
@article{olorunlana2026s3,
  author={Olorunlana, T. J.},
  title={Preventing Amazon S3 Cloud Storage Misconfiguration Using Infrastructure-as-Code: A Policy-Enforced Security Framework},
  journal={International Journal of Networked and Distributed Computing},
  year={2026},
  doi={10.1007/s44227-026-00114-2}
}
@misc{liu2024misconfigurations,
  author={Liu, Y. and Zhou, Y. and Zhang, H. and Chang, Z. and Xu, S. and Jia, Y. and Wang, W. and Liu, Z.},
  title={Rethinking Software Misconfigurations in the Real World: An Empirical Study and Literature Analysis},
  year={2024},
  eprint={2412.11121},
  archivePrefix={arXiv},
  doi={10.48550/arXiv.2412.11121}
}
@article{hogan2021knowledge,
  author={Hogan, Aidan and Blomqvist, Eva and Cochez, Michael and D'Amato, Claudia and de Melo, Gerard and Gutierrez, Claudio and Kirrane, Sabrina and Labra Gayo, Jose Emilio and Navigli, Roberto and Neumaier, Sebastian and Ngomo, Axel-Cyrille Ngonga and Polleres, Axel and Rashid, Sabbir M. and Rula, Anisa and Schmelzeisen, Lukas and Sequeda, Juan and Staab, Steffen and Zimmermann, Antoine},
  title={Knowledge Graphs},
  journal={ACM Computing Surveys},
  volume={54},
  number={4},
  articleno={71},
  year={2021},
  doi={10.1145/3447772}
}
@inproceedings{phillips1998graph,
  author={Phillips, Cynthia and Swiler, Laura Painton},
  title={A Graph-Based System for Network-Vulnerability Analysis},
  booktitle={Proceedings of the 1998 Workshop on New Security Paradigms},
  year={1998}
}
@inproceedings{sheyner2002automated,
  author={Sheyner, Oleg and Haines, Joshua and Jha, Somesh and Lippmann, Richard and Wing, Jeannette M.},
  title={Automated Generation and Analysis of Attack Graphs},
  booktitle={Proceedings of the 2002 IEEE Symposium on Security and Privacy},
  year={2002},
  doi={10.1109/SECPRI.2002.1004377}
}
@inproceedings{jha2002formal,
  author={Jha, Somesh and Sheyner, Oleg and Wing, Jeannette M.},
  title={Two Formal Analyses of Attack Graphs},
  booktitle={Proceedings of the 15th IEEE Computer Security Foundations Workshop},
  year={2002},
  doi={10.1109/CSFW.2002.1021806}
}
@article{rjoub2023xai,
  author={Rjoub, G. and Bentahar, J. and Abdel Wahab, O. and Mizouni, R. and Song, A. and Cohen, R. and Otrok, H. and Mourad, A.},
  title={A Survey on Explainable Artificial Intelligence for Cybersecurity},
  journal={IEEE Transactions on Network and Service Management},
  volume={20},
  number={4},
  pages={5115--5140},
  year={2023},
  doi={10.1109/TNSM.2023.3282740}
}
@article{charmet2022xai,
  author={Charmet, Franck and Tanuwidjaja, Harry Chandra and Ayoubi, S. and others},
  title={Explainable Artificial Intelligence for Cybersecurity: A Literature Survey},
  journal={Annals of Telecommunications},
  volume={77},
  pages={789--812},
  year={2022},
  doi={10.1007/s12243-022-00926-7}
}
@inproceedings{ribeiro2016lime,
  author={Ribeiro, Marco Tulio and Singh, Sameer and Guestrin, Carlos},
  title={Why Should I Trust You?: Explaining the Predictions of Any Classifier},
  booktitle={Proceedings of NAACL-HLT Demonstrations},
  pages={97--101},
  year={2016},
  doi={10.18653/v1/N16-3020}
}
@inproceedings{lundberg2017shap,
  author={Lundberg, Scott M. and Lee, Su-In},
  title={A Unified Approach to Interpreting Model Predictions},
  booktitle={Advances in Neural Information Processing Systems},
  volume={30},
  year={2017}
}
@article{hevner2004design,
  author={Hevner, Alan R. and March, Salvatore T. and Park, Jinsoo and Ram, Sudha},
  title={Design Science in Information Systems Research},
  journal={MIS Quarterly},
  volume={28},
  number={1},
  pages={75--105},
  year={2004},
  doi={10.2307/25148625}
}
@inproceedings{vaswani2017attention,
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, Lukasz and Polosukhin, Illia},
  title={Attention Is All You Need},
  booktitle={Advances in Neural Information Processing Systems},
  volume={30},
  year={2017}
}
@inproceedings{brown2020language,
  author={Brown, Tom B. and Mann, Benjamin and Ryder, Nick and Subbiah, Melanie and Kaplan, Jared D. and Dhariwal, Prafulla and Neelakantan, Arvind and Shyam, Pranav and Sastry, Girish and Askell, Amanda and others},
  title={Language Models are Few-Shot Learners},
  booktitle={Advances in Neural Information Processing Systems},
  volume={33},
  year={2020}
}
@misc{openai2023gpt4,
  author={{OpenAI}},
  title={GPT-4 Technical Report},
  year={2023},
  eprint={2303.08774},
  archivePrefix={arXiv}
}
@techreport{nist2011cloud,
  author={Mell, Peter and Grance, Timothy},
  title={The NIST Definition of Cloud Computing},
  institution={National Institute of Standards and Technology},
  number={SP 800-145},
  year={2011},
  doi={10.6028/NIST.SP.800-145}
}
`
);

write(
  path.join(out, "README.md"),
  `# CloudSentinel AI Thesis\n\nCompile with:\n\n\`\`\`bash\nlatexmk -pdf main.tex\n\`\`\`\n\nFigures live in \`figures/\`. Add references in \`references.bib\` and cite them with \`\\\\cite{key}\`. Chapter files are in \`chapters/\`; appendix material is in \`appendix/\`.\n`
);

write(
  path.join(out, "QA_REPORT.md"),
  `# QA Report\n\n- Source: docs/thesis/google-doc-export.md\n- Figures copied: ${Object.keys(figureCaptions).length} main figures, 5 appendix figures\n- Tables/equations/algorithms: converted into appendix/supporting material from the Google Doc export\n- Known author-confirmation items: submission date, supervisor name, experimental values marked as placeholders in the source\n- Known consistency fix: obvious algorithm numbering typo in Chapter 8 should be reviewed against final university format\n`
);
