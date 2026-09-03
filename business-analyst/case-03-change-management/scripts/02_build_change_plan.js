const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, BorderStyle, AlignmentType, ShadingType, Header, Footer, PageNumber,
} = require("docx");
const fs = require("fs");
const path = require("path");

const ACCENT = "44603B";
const INK_SOFT = "52514E";
const LINE = "D6DCDA";

const cellBorders = {
  top: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  bottom: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  left: { style: BorderStyle.SINGLE, size: 2, color: LINE },
  right: { style: BorderStyle.SINGLE, size: 2, color: LINE },
};

function h1(text) { return new Paragraph({ text, heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 } }); }
function body(text, opts = {}) {
  return new Paragraph({ children: [new TextRun({ text, ...opts })], spacing: { after: 160 } });
}
function bullet(text) { return new Paragraph({ text, bullet: { level: 0 }, spacing: { after: 80 } }); }

function headerCell(text, widthPct) {
  return new TableCell({
    width: { size: widthPct, type: WidthType.PERCENTAGE },
    shading: { type: ShadingType.CLEAR, fill: ACCENT },
    borders: cellBorders,
    margins: { top: 90, bottom: 90, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 16 })] })],
  });
}
function dataCell(text, widthPct, opts = {}) {
  return new TableCell({
    width: { size: widthPct, type: WidthType.PERCENTAGE },
    borders: cellBorders,
    margins: { top: 90, bottom: 90, left: 100, right: 100 },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    children: [new Paragraph({ children: [new TextRun({ text, size: 16, bold: !!opts.bold })] })],
  });
}
function table(headers, rows, widths) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: widths.map((w) => Math.round(w * 90)),
    rows: [
      new TableRow({ children: headers.map((h, i) => headerCell(h, widths[i])) }),
      ...rows.map((r, ri) => new TableRow({
        children: r.map((c, i) => dataCell(c, widths[i], { fill: ri % 2 === 1 ? "F3F5F4" : undefined })),
      })),
    ],
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Calibri", size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: ACCENT, font: "Calibri" }, paragraph: { spacing: { before: 320, after: 160 } } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
    headers: { default: new Header({ children: [new Paragraph({
      children: [new TextRun({ text: "Brightpath Distribution — Change Management Plan", size: 16, color: INK_SOFT })],
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE, space: 4 } },
    })] }) },
    footers: { default: new Footer({ children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: "Page ", size: 16, color: INK_SOFT }),
        new TextRun({ children: [PageNumber.CURRENT], size: 16, color: INK_SOFT }),
        new TextRun({ text: " of ", size: 16, color: INK_SOFT }),
        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: INK_SOFT }),
      ],
    })] }) },
    children: [
      new Paragraph({ children: [new TextRun({ text: "CHANGE MANAGEMENT PLAN", bold: true, size: 40, color: ACCENT })], spacing: { after: 80 } }),
      new Paragraph({ children: [new TextRun({ text: "Colton Regional Supply Warehouse Integration", size: 26, color: INK_SOFT })], spacing: { after: 240 } }),

      table(["Field", "Detail"], [
        ["Project sponsor", "COO"],
        ["Change lead", "HR Director"],
        ["Prepared by", "Business Analyst — Change Management"],
        ["Status", "Approved — integration in progress"],
        ["Scope", "Warehouse operations integration, 2 Colton sites into Brightpath operations"],
      ], [30, 70]),
      new Paragraph({ text: "", spacing: { after: 200 } }),
      new Paragraph({
        children: [new TextRun({
          text: "This is a simulated case study built for a business-analyst portfolio. Brightpath Distribution, Colton Regional Supply, and the details below are illustrative; the stakeholder analysis and RACI model behind this plan are real and reproducible — see stakeholder_analysis.xlsx.",
          italics: true, size: 17, color: INK_SOFT,
        })],
        spacing: { after: 200 },
        border: { left: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
      }),

      h1("1. Background"),
      body("Brightpath Distribution acquired Colton Regional Supply, a smaller regional distributor with two warehouse sites and roughly 85 employees, six weeks ago. The two companies' warehouse operations must integrate onto a single WMS, a single shift/scheduling policy, and a single reporting structure within four months, without disrupting order fulfillment for either customer base. The acquisition was announced to Colton employees only at signing; how the integration is run from here will determine whether it reads as a partnership or a takeover."),

      h1("2. Change Impact Assessment"),
      table(["Change area", "Who's affected", "Impact", "Current readiness"], [
        ["Warehouse management system (WMS)", "Colton warehouse staff & ops managers (Brightpath system replaces Colton's)", "High", "Low — no exposure to the new system yet"],
        ["Reporting lines", "Colton Ops Managers (now report into Brightpath VP Ops)", "High", "Medium — expected, but structure not yet finalized"],
        ["Shift & scheduling policy", "All warehouse staff, both sites", "Medium", "Medium — some policies already similar"],
        ["Safety & incident-reporting procedures", "All warehouse staff, both sites", "Medium", "High — procedural, less identity-charged"],
        ["Payroll & benefits harmonization", "All Colton staff", "High", "Low — financially sensitive, not yet communicated in detail"],
        ["Colton brand/identity", "Colton staff and long-standing Colton customers", "Medium (symbolic)", "Low — tied directly to job-security anxiety"],
      ], [26, 30, 12, 32]),

      h1("3. Stakeholder Engagement Approach"),
      body("Full detail in stakeholder_analysis.xlsx and the accompanying power/interest map. In summary, by quadrant:"),
      bullet("Manage Closely (COO, VP Ops, Colton GM, HR Director) — weekly working sessions; co-own every major decision jointly, not unilaterally from the Brightpath side."),
      bullet("Keep Informed (both sites' Ops Managers and warehouse staff) — the group carrying the most day-to-day disruption and the least formal power. Two-way channels, not announcements: town halls with open Q&A, and a standing channel for questions that gets answered within 48 hours, tracked and visible."),
      bullet("Keep Satisfied (CEO, key Colton-region customers) — periodic milestone updates; protect their confidence without pulling them into operational detail they don't need."),
      bullet("Monitor (IT, Finance/Payroll, general customer base) — kept current through standing project channels; escalate to Manage Closely only if a specific issue in their area surfaces."),
      body("The single biggest resistance risk identified in stakeholder interviews was asymmetric treatment: Colton staff explicitly worried about being folded into Brightpath's way of doing things with no input, versus a genuine two-way integration. Every activity in the accompanying RACI matrix mirrors Colton and Brightpath roles at each level deliberately, for this reason."),

      h1("4. Communication Plan"),
      table(["Phase", "Audience", "Message", "Channel", "Frequency", "Owner"], [
        ["1. Announcement (Wk 1)", "All staff, both companies", "What's changing, what isn't, and what happens next", "All-hands town hall + written FAQ", "Once, live", "COO + Colton GM (joint)"],
        ["2. Discovery & listening (Wk 2-3)", "Warehouse staff & ops managers, both sites", "We want your input on how this actually works day to day", "Small-group listening sessions", "2x per site", "HR Director + local Ops Managers"],
        ["3. Design & co-creation (Wk 4-8)", "Ops managers, IT, HR", "Here's what we heard and how it shaped the design", "Working sessions + biweekly written update", "Biweekly", "VP Ops + Colton GM"],
        ["4. Pre-go-live (Wk 9-10)", "All warehouse staff", "What your first day on the new system looks like, concretely", "Team briefings + one-page cutover guide", "Weekly", "Local Ops Managers"],
        ["5. Go-live (Wk 11)", "All warehouse staff", "Real-time support during cutover", "On-floor support + hotline", "Continuous, cutover weekend", "IT Lead + Ops Managers"],
        ["6. Reinforcement (Wk 12-16)", "All staff", "What's working, what we're still fixing, and how to raise an issue", "Biweekly written update", "Biweekly", "HR Director"],
      ], [17, 17, 26, 18, 10, 12]),

      h1("5. Training Plan"),
      table(["Audience", "Topic", "Format", "Timing"], [
        ["Colton warehouse staff", "New WMS — daily-use functions", "Hands-on, in small groups, on the actual warehouse floor", "Weeks 9-10, before go-live"],
        ["Colton Ops Managers", "New WMS — full administrative functions + reporting", "Instructor-led, remote or on-site", "Weeks 7-8"],
        ["Brightpath warehouse staff", "Any workflow changes from the harmonized shift/scheduling policy", "Team briefing", "Weeks 9-10"],
        ["All warehouse staff, both sites", "Unified safety & incident-reporting procedure", "In-person briefing + posted quick-reference card", "Week 9"],
      ], [24, 34, 26, 16]),

      h1("6. Resistance Risk Register"),
      table(["Risk", "Likelihood", "Impact", "Mitigation"], [
        ["Colton staff perceive the integration as a takeover, not a partnership", "High", "High", "Joint ownership of every major decision by the Colton GM and Brightpath VP Ops; mirrored roles in the RACI matrix; Colton GM co-delivers the announcement, not just Brightpath leadership."],
        ["Key Colton warehouse staff leave before cutover, straining fulfillment", "Medium", "High", "Retention conversations with named at-risk individuals (identified by local Ops Managers) before the announcement goes company-wide; competitive-with-Brightpath compensation confirmed early, not left ambiguous through the transition."],
        ["Brightpath Ops Managers treat their own processes as the default without genuine two-way design", "Medium", "Medium", "Design sessions explicitly structured to start from \"what works well at each site today,\" not \"how Brightpath already does it\"; HR Director sits in on design sessions specifically to check for this pattern."],
        ["Training doesn't stick and staff revert to old workarounds after go-live", "Medium", "Medium", "On-floor support continues for two full weeks post-cutover, not just cutover weekend itself; 30-day review (Section 8) explicitly checks adoption, not just system uptime."],
      ], [30, 12, 12, 46]),

      h1("7. Adoption Success Metrics"),
      table(["Metric", "Target"], [
        ["Staff attendance at listening sessions (Phase 2)", "≥ 80% of warehouse staff, both sites"],
        ["Voluntary turnover, Colton sites, during the integration window", "No increase over the trailing 12-month baseline rate"],
        ["WMS daily active use rate, both sites, 30 days post-go-live", "≥ 95% of transactions logged in the new system, not the old one or a workaround spreadsheet"],
        ["Unresolved staff questions in the standing Q&A channel, older than 48 hours", "Zero, tracked weekly"],
        ["Order fulfillment accuracy, both sites, during cutover week", "No degradation versus the trailing 8-week average"],
      ], [58, 42]),

      h1("8. Approval"),
      table(["Role", "Name", "Signature", "Date"], [
        ["Project Sponsor (COO)", "", "", ""],
        ["Change Lead (HR Director)", "", "", ""],
        ["Business Analyst", "", "", ""],
      ], [30, 25, 25, 20]),
    ],
  }],
});

const outPath = path.join(__dirname, "..", "artifacts", "change_management_plan.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log("Saved", outPath); });
